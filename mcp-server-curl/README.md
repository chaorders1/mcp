# MCP Curl

A Model Context Protocol (MCP) server that enables executing curl commands through natural language requests. This service acts as a bridge between natural language processing capabilities and curl's command-line interface.

## Components

### Modular Handlers

The server implements a modular handler system for different API services:

1. Railway Handlers:
   - `railway-health`: Check health status of Railway.app service
   - `railway-process-file`: Process files through Railway.app API

2. Ollama Handler:
   - `ollama-generate`: Generate text using Ollama models
   - Supports model selection, temperature control, and streaming

3. Firecrawl Handler:
   - `firecrawl-scrape`: Web scraping operations
   - Supports multiple output formats (markdown, html, links)

### Adding New Handlers

The server uses a plugin-like architecture for handlers. To add a new handler:

1. Create a new handler class in the `handlers` directory
2. Inherit from `CurlHandler` base class
3. Implement required methods:
   - `name`: Handler identifier
   - `description`: Handler description
   - `input_schema`: JSON Schema for inputs
   - `build_curl_command`: Method to construct curl command

## Requirements

- Python 3.10 or higher
- curl command-line tool
- Internet connection for API access

## Configuration

### Environment Variables

The server uses `.env` file for configuration:
```bash
# Ollama configuration
OLLAMA_API_URL=http://127.0.0.1:11434  # Optional

# Railway.app configuration
RAILWAY_API_TOKEN=your_railway_token_here
RAILWAY_API_URL=your_railway_url  # Optional

# Firecrawl configuration
FIRECRAWL_API_KEY=your_firecrawl_key_here
```

## Quickstart

### Install

```bash
pip install mcp-server-curl
```

The package will automatically:
1. Set up all required Python dependencies
2. Configure default handlers
3. Prepare for API interactions

#### Claude Desktop Configuration

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```json
  "mcpServers": {
    "mcp-server-curl": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yuanlu/Code/mcp/mcp-server-curl",
        "run",
        "mcp-server-curl"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```json
  "mcpServers": {
    "mcp-server-curl": {
      "command": "uvx",
      "args": [
        "mcp-server-curl"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Adding New Handlers

To add a new handler:

1. Create a new file in `handlers` directory:
```python
import os
import json
from typing import Any, Dict, List, Optional
from . import CurlHandler

class MyNewHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "my-new-handler"
    
    @property
    def description(self) -> str:
        return "Description of my new handler"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                # Define your input schema
            },
            "required": [],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        # Build and return curl command as a list of strings
        return [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "--fail-with-body",
            # Add more curl options as needed
            "your-api-url"
        ]
```

2. Register the handler in `server.py`:
```python
from .handlers.my_new import MyNewHandler

class CurlServer:
    def __init__(self):
        self.handlers: Dict[str, CurlHandler] = {}
        self._register_handlers([
            # ... existing handlers ...
            MyNewHandler()
        ])
```

### Testing

To run the test client:
```bash
mcp-server-curl-client
```

The client will perform test operations using the registered handlers.

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/yuanlu/Code/mcp/mcp-server-curl run mcp-server-curl
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.