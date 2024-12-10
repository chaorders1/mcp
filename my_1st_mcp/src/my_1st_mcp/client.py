import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
import mcp.types as types

async def run_client():
    # Load environment variables from .env file
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(env_path)
    
    # Check for Anthropic API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY environment variable not set.")
        print("Claude integration will not be available.")
        print("Please create a .env file in the project root with:")
        print("ANTHROPIC_API_KEY=your_api_key")
    
    # Set up environment with API key
    env = {
        "ANTHROPIC_API_KEY": api_key
    } if api_key else None
    
    # Connect to the MCP server
    server_params = StdioServerParameters(
        command="my-1st-mcp",  # This should match your project.scripts entry
        args=[],
        env=env  # Pass the environment with API key
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Example: Add a note using the tool
            result = await session.call_tool(
                "add-note", 
                {
                    "name": "test",
                    "content": "This is a test note"
                }
            )
            print("Added note:", result)
            
            # Example: List all resources (notes)
            resources = await session.list_resources()
            print("Available resources:", resources)
            
            # Example: Get and use a prompt
            prompts = await session.list_prompts()
            print("Available prompts:", prompts)
            
            if prompts:
                prompt = await session.get_prompt("summarize-notes", {"style": "detailed"})
                print("Prompt result:", prompt)

def main():
    asyncio.run(run_client())

if __name__ == "__main__":
    main() 