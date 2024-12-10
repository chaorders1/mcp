# MCP Curl

A Model Context Protocol (MCP) server that enables executing curl commands through natural language requests. This service acts as a bridge between natural language processing capabilities and curl's command-line interface.

## Components

### Resources

The server implements curl operations with:
- Custom curl:// URI scheme for accessing operation status
- Each operation resource has an ID, status, and response information
- Supports tracking of HTTP requests and responses
- Pre-configured templates for common API services

### Tools

The server implements several main tools:

1. ollama-generate: Generate text using Ollama models
   - Takes "model" and "prompt" as required arguments
   - Supports temperature parameter for generation control

2. firecrawl-scrape: Web scraping operations
   - Takes "url" as required argument
   - Supports multiple output formats

3. railway-process: Process files through Railway.app
   - Takes "file_path" as required argument
   - Supports various processing options

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
2. Configure default templates
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

### Testing

To run the test client:
```bash
mcp-server-curl-client
```

The client will perform test operations including:
1. Ollama text generation
2. Firecrawl web scraping
3. Railway.app file processing

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/yuanlu/Code/mcp/mcp-server-curl run mcp-server-curl
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.