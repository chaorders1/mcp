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
    
    # Copy the source video to work directory
    source_video = Path("/Users/yuanlu/Code/mcp/mcp_ffmpeg/video.mp4")
    target_video = work_dir / "video.mp4"
    shutil.copy2(source_video, target_video)
    print(f"Copied test video to {target_video}")
    
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
            
            # Test 1: Convert video to different format (MP4 to MOV)
            print("\nTest 1: Converting MP4 to MOV...")
            result = await session.call_tool(
                "convert-media", 
                {
                    "input_file": "video.mp4",
                    "output_format": "mov"
                }
            )
            print("Conversion result:", result)
            
            # Test 2: Extract audio from video
            print("\nTest 2: Extracting audio...")
            result = await session.call_tool(
                "extract-audio",
                {
                    "input_file": "video.mp4"
                }
            )
            print("Audio extraction result:", result)
            
            # Test 3: List all operations
            print("\nTest 3: Listing operations...")
            resources = await session.list_resources()
            print("Available operations:", resources)
            
            print("\nTest files can be found in:", work_dir)

def main():
    asyncio.run(run_client())

if __name__ == "__main__":
    main() 