import asyncio
import logging
from typing import Dict, List
from pathlib import Path
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from dotenv import load_dotenv

from .handlers import CurlHandler
from .handlers.railway import RailwayHealthHandler, RailwayProcessFileHandler, RailWayYoutubeChanelAnalyzeHandler, RailWayAnalyzeStatusHandler
from .handlers.ollama import OllamaGenerateHandler
from .handlers.firecrawl import FirecrawlScrapeHandler

class CurlServer:
    def __init__(self):
        self.handlers: Dict[str, CurlHandler] = {}
        self._register_handlers([
            RailwayHealthHandler(),
            RailwayProcessFileHandler(),
            RailWayYoutubeChanelAnalyzeHandler(),
            RailWayAnalyzeStatusHandler(),
            OllamaGenerateHandler(),
            FirecrawlScrapeHandler()
        ])
    
    def _register_handlers(self, handlers: List[CurlHandler]):
        for handler in handlers:
            self.handlers[handler.name] = handler
    
    def get_tools(self) -> List[types.Tool]:
        """Get all available tools"""
        return [handler.get_tool_definition() for handler in self.handlers.values()]
    
    async def call_tool(self, name: str, arguments: Dict) -> Dict:
        """Call a tool by name with arguments"""
        handler = self.handlers.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")
            
        return await handler.handle(arguments)

server = Server("curl-mcp")

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available curl operations."""
    return curl_server.get_tools()

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Dict | None
) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls for curl operations"""
    try:
        result = await curl_server.call_tool(name, arguments or {})
        return [types.TextContent(type="text", text=str(result))]
    except Exception as e:
        logging.error(f"Error handling tool call: {e}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the server
    global curl_server
    curl_server = CurlServer()
    
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

if __name__ == "__main__":
    asyncio.run(main())