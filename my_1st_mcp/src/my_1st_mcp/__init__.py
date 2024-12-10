"""
A simple MCP server and client implementation that demonstrates note-taking functionality.
"""

from .server import main as server_main
from .client import main as client_main

__all__ = ["server_main", "client_main"]