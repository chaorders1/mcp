"""
MCP FFmpeg - A Model Context Protocol server for FFmpeg operations.
Provides a natural language interface to common FFmpeg tasks like media conversion and audio extraction.
"""

from .server import main as server_main
from .client import main as client_main

__all__ = ["server_main", "client_main"]