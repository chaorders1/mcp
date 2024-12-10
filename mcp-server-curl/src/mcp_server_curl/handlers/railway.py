import os
from typing import Any, Dict, List, Optional
import json
from . import CurlHandler

class RailwayHealthHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "railway-health"
    
    @property
    def description(self) -> str:
        return "Check health status of Railway.app service"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        base_url = os.getenv("RAILWAY_API_URL", "https://railway.app")
        url = f"{base_url}/health"
        
        return [
            "curl",
            "-X", "GET",
            "-H", "Content-Type: application/json",
            "--fail-with-body",
            url
        ]

class RailwayProcessFileHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "railway-process-file"
    
    @property
    def description(self) -> str:
        return "Process a file using Railway.app API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to process (e.g., data/example.md)"
                },
                "format": {
                    "type": "string",
                    "optional": True,
                    "description": "Output format for the processed file"
                },
                "options": {
                    "type": "object",
                    "optional": True,
                    "description": "Additional processing options"
                },
            },
            "required": ["file_path"],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        file_path = arguments.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")
            
        base_url = os.getenv("RAILWAY_API_URL", "https://railway.app")
        url = f"{base_url}/file"
        
        data = {"file_path": file_path}
        if "format" in arguments:
            data["format"] = arguments["format"]
        if "options" in arguments:
            data["options"] = arguments["options"]
            
        command = [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "--fail-with-body",
            "-d", json.dumps(data),
            url
        ]
        
        return command 

class RailWayYoutubeChanelAnalyzeHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "railway-youtube-channel-analyze"
    
    @property
    def description(self) -> str:
        return "Analyze a YouTube channel using Railway.app API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "youtube_channel_url": {
                    "type": "string",
                    "description": "URL of the YouTube channel to analyze"
                }
            },
            "required": ["youtube_channel_url"],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        channel_url = arguments.get("youtube_channel_url")
        if not channel_url:
            raise ValueError("youtube_channel_url is required")
            
        base_url = os.getenv("RAILWAY_API_URL", "https://railway1-production-9936.up.railway.app")
        url = f"{base_url}/analyze"
        
        data = {"youtube_channel_url": channel_url}
            
        command = [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "-H", "accept: application/json",
            "--fail-with-body",
            "-d", json.dumps(data),
            url
        ]
        
        return command

class RailWayAnalyzeStatusHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "railway-analyze-status"
    
    @property
    def description(self) -> str:
        return "Check the status of a YouTube channel analysis task"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "Task ID of the analysis to check"
                }
            },
            "required": ["task_id"],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        task_id = arguments.get("task_id")
        if not task_id:
            raise ValueError("task_id is required")
            
        base_url = os.getenv("RAILWAY_API_URL", "https://railway1-production-9936.up.railway.app")
        url = f"{base_url}/analyze/status?task_id={task_id}"
        
        command = [
            "curl",
            "-X", "POST",
            "-H", "accept: application/json",
            "--fail-with-body",
            "-d", "",
            url
        ]
        
        return command