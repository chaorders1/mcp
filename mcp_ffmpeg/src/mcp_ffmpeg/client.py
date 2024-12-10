import asyncio
import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import mcp.types as types

async def run_client():
    # Set up the work directory for media files
    work_dir = Path.home() / ".mcp-ffmpeg"
    work_dir.mkdir(exist_ok=True)
    
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="mcp-ffmpeg",  # This matches our project.scripts entry
        args=[],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            return session

def main():
    asyncio.run(run_client())

if __name__ == "__main__":
    main() 