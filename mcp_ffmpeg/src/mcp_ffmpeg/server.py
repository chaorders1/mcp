import asyncio
import os
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

@dataclass
class FFmpegOperation:
    id: str
    status: str = "pending"
    input_file: str = ""
    output_file: str = ""
    command: list[str] = None
    progress: float = 0.0

class FFmpegWrapper:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.operations: dict[str, FFmpegOperation] = {}
        
    def validate_ffmpeg(self) -> bool:
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
            
    def _create_operation(self, op_type: str, input_path: Path, output_path: Path, 
                         command: list[str]) -> FFmpegOperation:
        """Helper method to reduce code duplication in operation creation"""
        operation_id = f"{op_type}_{len(self.operations)}"
        operation = FFmpegOperation(
            id=operation_id,
            input_file=str(input_path),
            output_file=str(output_path),
            command=command
        )
        self.operations[operation_id] = operation
        return operation

    async def convert_media(self, input_file: str, output_format: str) -> FFmpegOperation:
        input_path = self.work_dir / input_file
        output_file = input_path.with_suffix(f".{output_format}")
        command = ["ffmpeg", "-i", str(input_path), "-y", str(output_file)]
        return self._create_operation("conv", input_path, output_file, command)
        
    async def extract_audio(self, input_file: str) -> FFmpegOperation:
        input_path = self.work_dir / input_file
        output_file = input_path.with_suffix(".mp3")
        command = [
            "ffmpeg", "-i", str(input_path),
            "-vn", "-acodec", "libmp3lame", "-y",
            str(output_file)
        ]
        return self._create_operation("audio", input_path, output_file, command)

# Initialize the FFmpeg wrapper with a work directory
work_dir = Path.home() / ".mcp-ffmpeg"
work_dir.mkdir(exist_ok=True)
ffmpeg = FFmpegWrapper(work_dir)

server = Server("ffmpeg-mcp")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available media operations and their status."""
    return [
        types.Resource(
            uri=AnyUrl(f"ffmpeg://operation/{op.id}"),
            name=f"Operation: {op.id}",
            description=f"FFmpeg operation: {' '.join(op.command)}",
            mimeType="application/json",
        )
        for op in ffmpeg.operations.values()
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """Read operation status by its URI."""
    if uri.scheme != "ffmpeg":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    op_id = uri.path.lstrip("/")
    if op_id in ffmpeg.operations:
        op = ffmpeg.operations[op_id]
        return f"Status: {op.status}\nProgress: {op.progress:.1f}%\nCommand: {' '.join(op.command)}"
    raise ValueError(f"Operation not found: {op_id}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available FFmpeg operations."""
    return [
        types.Tool(
            name="convert-media",
            description="Convert media file to different format",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string"},
                    "output_format": {"type": "string"},
                },
                "required": ["input_file", "output_format"],
            },
        ),
        types.Tool(
            name="extract-audio",
            description="Extract audio from video file",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {"type": "string"},
                },
                "required": ["input_file"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Simplified tool handler"""
    if not ffmpeg.validate_ffmpeg():
        return [types.TextContent(type="text", 
                text="Error: FFmpeg is not installed or not accessible")]

    if not arguments:
        return [types.TextContent(type="text", text="Error: Missing arguments")]

    try:
        operation = None
        if name == "convert-media":
            input_file = arguments.get("input_file")
            output_format = arguments.get("output_format")
            if not input_file or not output_format:
                raise ValueError("Missing input_file or output_format")
            operation = await ffmpeg.convert_media(input_file, output_format)
            
        elif name == "extract-audio":
            input_file = arguments.get("input_file")
            if not input_file:
                raise ValueError("Missing input_file")
            operation = await ffmpeg.extract_audio(input_file)
        else:
            return [types.TextContent(type="text", 
                    text=f"Error: Unknown tool: {name}")]

        # Execute FFmpeg operation
        process = await asyncio.create_subprocess_exec(
            *operation.command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        operation.status = "running"
        await process.wait()
        operation.status = "completed" if process.returncode == 0 else "failed"
        operation.progress = 100.0 if process.returncode == 0 else 0.0
        
        await server.request_context.session.send_resource_list_changed()
        return [types.TextContent(type="text", 
                text=f"Operation {operation.id} {operation.status}")]
            
    except Exception as e:
        if operation:
            operation.status = "failed"
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

def main():
    async def run():
        # Ensure work directory exists
        work_dir = Path.home() / ".mcp-ffmpeg"
        work_dir.mkdir(exist_ok=True)
        
        # Initialize FFmpeg wrapper (this will trigger auto-installation if needed)
        global ffmpeg
        ffmpeg = FFmpegWrapper(work_dir)
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ffmpeg-mcp",
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