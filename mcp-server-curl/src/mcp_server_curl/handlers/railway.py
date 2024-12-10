import os
from typing import Any, Dict, List, Optional
import json
from . import CurlHandler

class RailwayHealthHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "railway-health"
    
    @property
    def description(self) -> str:
        return "Check health status of Railway.app service"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        base_url = os.getenv("RAILWAY_API_URL", "https://railway.app")
        url = f"{base_url}/health"
        
        return [
            "curl",
            "-X", "GET",
            "-H", "Content-Type: application/json",
            "--fail-with-body",
            url
        ]

class RailwayProcessFileHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "railway-process-file"
    
    @property
    def description(self) -> str:
        return "Process a file using Railway.app API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
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
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        file_path = arguments.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")
            
        base_url = os.getenv("RAILWAY_API_URL", "https://railway.app")
        url = f"{base_url}/file"
        
        data = {"file_path": file_path}
        if "format" in arguments:
            data["format"] = arguments["format"]
        if "options" in arguments:
            data["options"] = arguments["options"]
            
        command = [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "--fail-with-body",
            "-d", json.dumps(data),
            url
        ]
        
        return command 