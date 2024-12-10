import asyncio
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import os
from enum import Enum

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

class OperationError(Exception):
    """Base class for operation errors"""
    pass

class AuthenticationError(OperationError):
    """Raised when authentication fails"""
    pass

class TemplateError(OperationError):
    """Raised when there's an issue with a template"""
    pass

class ValidationError(OperationError):
    """Raised when validation fails"""
    pass

@dataclass
class CurlOperation:
    id: str
    status: str = "pending"
    template: str = ""  # Template name if used
    url: str = ""
    method: str = "GET"
    headers: Dict[str, str] = None
    data: Any = None
    command: list[str] = None
    response: str = ""
    error: Optional[str] = None

class TemplateManager:
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.templates = {
            "ollama": {
                "base_url": "http://127.0.0.1:11434",
                "endpoints": {
                    "generate": "/api/generate",
                    "list": "/api/tags",
                    "pull": "/api/pull"
                }
            },
            "firecrawl": {
                "base_url": "https://api.firecrawl.dev/v1",
                "endpoints": {
                    "scrape": "/scrape"
                },
                "auth_type": "Bearer",
                "auth_env_key": "FIRECRAWL_API_KEY"
            },
            "railway": {
                "base_url": os.getenv("RAILWAY_API_URL", "https://railway1-production-9936.up.railway.app"),
                "endpoints": {
                    "file": "/file",
                    "status": "/status"
                }
            }
        }
    
    def get_template(self, name: str) -> dict:
        template = self.templates.get(name)
        if not template:
            raise TemplateError(f"Template not found: {name}")
        return template

    def validate_auth(self, template_name: str) -> None:
        """Validate authentication for a template"""
        template = self.get_template(template_name)
        if "auth_type" in template:
            if template["auth_type"] == "Bearer":
                env_key = template.get("auth_env_key")
                if env_key and not os.getenv(env_key):
                    raise AuthenticationError(
                        f"Missing authentication token for {template_name}. "
                        f"Please set {env_key} environment variable."
                    )

class CurlWrapper:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.operations: dict[str, CurlOperation] = {}
        self.template_manager = TemplateManager(work_dir / "templates")
        
    def validate_curl(self) -> bool:
        try:
            subprocess.run(["curl", "--version"], capture_output=True, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _create_operation(self, template: str, url: str, method: str,
                         headers: Dict[str, str] = None, 
                         data: Any = None) -> CurlOperation:
        operation_id = f"curl_{len(self.operations)}"
        command = ["curl", "-X", method, "--fail-with-body"]  # Add --fail-with-body for better error handling
        
        if headers:
            for key, value in headers.items():
                command.extend(["-H", f"{key}: {value}"])
        
        if data:
            if isinstance(data, dict):
                command.extend(["-d", json.dumps(data)])
            else:
                command.extend(["-d", str(data)])
        
        command.append(url)
        
        operation = CurlOperation(
            id=operation_id,
            template=template,
            url=url,
            method=method,
            headers=headers,
            data=data,
            command=command
        )
        self.operations[operation_id] = operation
        return operation

    async def execute_request(self, template: str, endpoint: str, 
                            method: str = "GET", 
                            headers: Dict[str, str] = None,
                            data: Any = None) -> CurlOperation:
        # Validate template and authentication
        tmpl = self.template_manager.get_template(template)
        self.template_manager.validate_auth(template)
        
        # Build URL
        base_url = tmpl["base_url"]
        url = f"{base_url}{endpoint}"
        
        # Add authentication headers if needed
        headers = headers or {}
        if tmpl.get("auth_type") == "Bearer":
            env_key = tmpl.get("auth_env_key")
            if env_key:
                token = os.getenv(env_key)
                headers["Authorization"] = f"Bearer {token}"
        
        return self._create_operation(template, url, method, headers, data)

# Initialize the Curl wrapper with a work directory
work_dir = Path.home() / ".mcp-server-curl"
work_dir.mkdir(exist_ok=True)
curl = CurlWrapper(work_dir)

server = Server("curl-mcp")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available curl operations and their status."""
    return [
        types.Resource(
            uri=AnyUrl(f"curl://operation/{op.id}"),
            name=f"Operation: {op.id}",
            description=f"Curl operation: {' '.join(op.command)}",
            mimeType="application/json",
        )
        for op in curl.operations.values()
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read operation status and response by its URI."""
    if uri.scheme != "curl":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    op_id = uri.path.lstrip("/")
    if op_id in curl.operations:
        op = curl.operations[op_id]
        error_info = f"\nError: {op.error}" if op.error else ""
        return f"Status: {op.status}\nResponse: {op.response}\nCommand: {' '.join(op.command)}{error_info}"
    raise ValueError(f"Operation not found: {op_id}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available curl operations."""
    return [
        types.Tool(
            name="ollama-generate",
            description="Generate text using Ollama API",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "default": "llama3.2:latest",
                        "description": "The model to use for text generation (default: llama3.2:latest)"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "The input text prompt for generation (required)"
                    },
                    "temperature": {
                        "type": "number",
                        "optional": True,
                        "default": 0.7,
                        "description": "Controls randomness in generation (0.0-1.0, default: 0.7)"
                    },
                    "stream": {
                        "type": "boolean",
                        "optional": True,
                        "default": False,
                        "description": "Whether to stream the response (default: false)"
                    },
                },
                "required": ["prompt"],
            },
        ),
        types.Tool(
            name="firecrawl-scrape",
            description="Scrape a webpage using Firecrawl API",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The webpage URL to scrape (required)"
                    },
                    "formats": {
                        "type": "array",
                        "optional": True,
                        "default": ["markdown"],
                        "items": {
                            "type": "string",
                            "enum": ["markdown", "html", "links"]
                        },
                        "description": "Available formats: markdown, html, links"
                    },
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="railway-process-file",
            description="Process a file using Railway.app API",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to process (e.g., data/example.md)"
                    },
                    "format": {
                        "type": "string",
                        "optional": True,
                        "description": "Output format for the processed file"
                    },
                    "options": {
                        "type": "object",
                        "optional": True,
                        "description": "Additional processing options"
                    },
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="railway-status",
            description="Check status of a Railway.app operation",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation_id": {"type": "string"},
                },
                "required": ["operation_id"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for curl operations"""
    if not curl.validate_curl():
        return [types.TextContent(type="text", 
                text="Error: curl is not installed or not accessible")]

    if not arguments:
        return [types.TextContent(type="text", text="Error: Missing arguments")]

    try:
        operation = None
        if name == "ollama-generate":
            model = arguments.get("model", "llama3.2:latest")
            prompt = arguments.get("prompt")
            if not prompt:
                raise ValidationError("Missing prompt")
            
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": arguments.get("temperature", 0.7),
                "stream": arguments.get("stream", False)
            }
                
            operation = await curl.execute_request(
                "ollama", 
                "/api/generate",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=data
            )
            
        elif name == "firecrawl-scrape":
            url = arguments.get("url")
            if not url:
                raise ValidationError("Missing url")
            
            data = {"url": url}
            if "formats" in arguments:
                data["formats"] = arguments["formats"]
                
            operation = await curl.execute_request(
                "firecrawl",
                "/scrape",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=data
            )
            
        elif name == "railway-process-file":
            file_path = arguments.get("file_path")
            if not file_path:
                raise ValidationError("Missing file_path")
            
            data = {"file_path": file_path}
            if "format" in arguments:
                data["format"] = arguments["format"]
            if "options" in arguments:
                data["options"] = arguments["options"]
                
            operation = await curl.execute_request(
                "railway",
                "/file",
                method="POST",
                headers={"Content-Type": "application/json"},
                data=data
            )
            
        elif name == "railway-status":
            operation_id = arguments.get("operation_id")
            if not operation_id:
                raise ValidationError("Missing operation_id")
                
            operation = await curl.execute_request(
                "railway",
                "/status",
                method="GET",
                headers={"Content-Type": "application/json"},
                data={"operation_id": operation_id}
            )
            
        else:
            return [types.TextContent(type="text", 
                    text=f"Error: Unknown tool: {name}")]

        # Execute curl operation with timeout
        try:
            process = await asyncio.create_subprocess_exec(
                *operation.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            operation.status = "running"
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=30.0  # 30 second timeout
                )
                operation.status = "completed" if process.returncode == 0 else "failed"
                if process.returncode == 0:
                    operation.response = stdout.decode()
                else:
                    operation.error = stderr.decode()
                    operation.response = stderr.decode()
            except asyncio.TimeoutError:
                operation.status = "timeout"
                operation.error = "Operation timed out after 30 seconds"
                try:
                    process.kill()
                except:
                    pass
        except Exception as e:
            operation.status = "failed"
            operation.error = str(e)
            operation.response = str(e)
        
        await server.request_context.session.send_resource_list_changed()
        
        if operation.error:
            return [types.TextContent(type="text", 
                    text=f"Operation {operation.id} {operation.status}\nError: {operation.error}")]
        return [types.TextContent(type="text", 
                text=f"Operation {operation.id} {operation.status}\n{operation.response}")]
            
    except (ValidationError, AuthenticationError, TemplateError) as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    except Exception as e:
        if operation:
            operation.status = "failed"
            operation.error = str(e)
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

def main():
    async def run():
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("Warning: python-dotenv not installed. Environment variables must be set manually.")
        
        # Ensure work directory exists
        work_dir = Path.home() / ".mcp-server-curl"
        work_dir.mkdir(exist_ok=True)
        
        # Initialize Curl wrapper
        global curl
        curl = CurlWrapper(work_dir)
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="curl-mcp",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                ),
            )
    
    asyncio.run(run())

if __name__ == "__main__":
    main()