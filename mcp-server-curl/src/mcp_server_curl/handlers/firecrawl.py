import os
import json
from typing import Any, Dict, List, Optional
from . import CurlHandler

class FirecrawlScrapeHandler(CurlHandler):
    # 90 seconds timeout for web scraping
    DEFAULT_TIMEOUT = 90
    
    @property
    def name(self) -> str:
        return "firecrawl-scrape"
    
    @property
    def description(self) -> str:
        return "Scrape a webpage using Firecrawl API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The webpage URL to scrape (required)"
                },
                "formats": {
                    "type": "array",
                    "optional": True,
                    "default": ["markdown"],
                    "items": {
                        "type": "string",
                        "enum": ["markdown", "html", "links"]
                    },
                    "description": "Available formats: markdown, html, links"
                }
            },
            "required": ["url"],
        }
    
    @property
    def timeout(self) -> float:
        """Allow longer timeout for web scraping"""
        return self.DEFAULT_TIMEOUT
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        url = arguments.get("url")
        if not url:
            raise ValueError("url is required")
            
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY environment variable is required")
            
        data = {"url": url}
        if "formats" in arguments:
            data["formats"] = arguments["formats"]
            
        # Add curl's own timeout option (in seconds)
        command = [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {api_key}",
            "--fail-with-body",
            # Add curl's max-time option
            "--max-time", str(self.timeout),
            "-d", json.dumps(data),
            "https://api.firecrawl.dev/v1/scrape"
        ]
        
        return command 