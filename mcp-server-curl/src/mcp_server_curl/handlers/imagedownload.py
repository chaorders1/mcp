import os
from typing import Any, Dict, List, Optional
from pathlib import Path
from . import CurlHandler

class ImageDownloadHandler(CurlHandler):
    # 30 seconds timeout for image download
    DEFAULT_TIMEOUT = 30
    
    @property
    def name(self) -> str:
        return "image-download"
    
    @property
    def description(self) -> str:
        return "Download an image from a given URL to a specified path (default: Desktop)"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The image URL to download (required). For example:https://upload.wikimedia.org/wikipedia/commons/c/ca/1911_Solvay_conference.jpg"
                },
                "output_path": {
                    "type": "string",
                    "description": "The path where to save the image. If not provided, will save to Desktop"
                }
            },
            "required": ["url"],
        }
    
    @property
    def timeout(self) -> float:
        """Allow reasonable timeout for image download"""
        return self.DEFAULT_TIMEOUT
    
    def _get_desktop_path(self) -> str:
        """Get the user's Desktop directory path"""
        return os.path.expanduser("~/Desktop")
    
    def _validate_path(self, path: str) -> str:
        """Validate and prepare the output path"""
        # Convert to absolute path if relative
        abs_path = os.path.expanduser(path)
        if not os.path.isabs(abs_path):
            abs_path = os.path.abspath(path)
            
        # Create directory if it doesn't exist
        directory = os.path.dirname(abs_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        return abs_path
    
    def _get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        return url.split('/')[-1].split('?')[0] or 'downloaded_image'
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        url = arguments.get("url")
        if not url:
            raise ValueError("url is required")
            
        output_path = arguments.get("output_path")
        
        # Basic curl command
        command = ["curl", "--fail-with-body", "--max-time", str(self.timeout)]
        
        if output_path:
            # If output path is provided, validate and use it
            validated_path = self._validate_path(output_path)
        else:
            # If no path provided, save to Desktop with original filename
            filename = self._get_filename_from_url(url)
            desktop_path = self._get_desktop_path()
            validated_path = os.path.join(desktop_path, filename)
            
        command.extend(["-o", validated_path])
        command.append(url)
        return command 