import os
import json
from typing import Any, Dict, List, Optional
from . import CurlHandler

class OpenAIChatHandler(CurlHandler):
    # Set timeout to 60 seconds for OpenAI API calls
    DEFAULT_TIMEOUT = 60
    
    @property
    def name(self) -> str:
        return "openai-chat"
    
    @property
    def description(self) -> str:
        return "Send requests to OpenAI's chat completions API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "description": "The OpenAI model to use (e.g., gpt-4, gpt-4o-mini)",
                    "default": "gpt-4o-mini"
                },
                "system_message": {
                    "type": "string",
                    "description": "System message to set the behavior",
                    "default": "You are a helpful assistant."
                },
                "user_message": {
                    "type": "string",
                    "description": "The user's message/prompt (required)"
                }
            },
            "required": ["user_message"],
        }
    
    @property
    def timeout(self) -> float:
        return self.DEFAULT_TIMEOUT
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        user_message = arguments.get("user_message")
        if not user_message:
            raise ValueError("user_message is required")
            
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        # Prepare the messages payload
        messages = [
            {
                "role": "system",
                "content": arguments.get("system_message", "You are a helpful assistant.")
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
        
        # Prepare the full request payload
        data = {
            "model": arguments.get("model", "gpt-4o-mini"),
            "messages": messages
        }
        
        command = [
            "curl",
            "https://api.openai.com/v1/chat/completions",
            "-H", "Content-Type: application/json",
            "-H", f"Authorization: Bearer {api_key}",
            "-d", json.dumps(data)
        ]
        
        # Add timeout for safety
        command.extend(["--max-time", str(self.timeout)])
        
        return command
    
    async def handle(self, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Parse the JSON response from OpenAI"""
        try:
            result = await super().handle(arguments)
            
            if isinstance(result, (str, bytes)):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse OpenAI response", "raw": str(result)}
            
            return result
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}",
                "status": "error",
                "details": "The request might have timed out or OpenAI service might be unavailable"
            } 