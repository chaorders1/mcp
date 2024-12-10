# MCP FFmpeg

A Model Context Protocol server for FFmpeg operations that enables Claude to execute FFmpeg commands through natural language requests.

## Components

### Resources

The server implements FFmpeg operations with:
- Custom ffmpeg:// URI scheme for accessing operation status
- Each operation resource has an ID, status, and command information
- Supports tracking of conversion and extraction operations

### Tools

The server implements two main tools:

1. convert-media: Convert media files between formats
   - Takes "input_file" and "output_format" as required arguments
   - Supports common video formats (mp4, mov, etc.)

2. extract-audio: Extract audio from video files
   - Takes "input_file" as required argument
   - Outputs MP3 audio format

## Requirements

- FFmpeg must be installed on the system
- Python 3.10 or higher
- macOS (currently supported platform)

## Configuration

### Working Directory

The server uses `~/.mcp-ffmpeg` as its working directory for:
- Input media files
- Output converted files
- Temporary processing files

### FFmpeg Installation

On macOS, install FFmpeg using Homebrew:
```bash
brew install ffmpeg
```

## Quickstart

### Install

```bash
pip install mcp-ffmpeg
```

#### Claude Desktop Configuration

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```json
  "mcpServers": {
    "mcp-ffmpeg": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yuanlu/Code/mcp/mcp_ffmpeg",
        "run",
        "mcp-ffmpeg"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```json
  "mcpServers": {
    "mcp-ffmpeg": {
      "command": "uvx",
      "args": [
        "mcp-ffmpeg"
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

This will create source and wheel distributions in the `dist/` directory.

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
mcp-ffmpeg-client
```

The client will perform test operations including:
1. Video format conversion
2. Audio extraction
3. Operation status listing

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/yuanlu/Code/mcp/mcp_ffmpeg run mcp-ffmpeg
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.