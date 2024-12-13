import os
import json
from typing import Any, Dict, List, Optional
from . import CurlHandler

class TemplateCurlHandler(CurlHandler):
    # Set your desired timeout in seconds
    DEFAULT_TIMEOUT = 30
    
    @property
    def name(self) -> str:
        # TODO: Replace with your handler name
        return "template-handler"
    
    @property
    def description(self) -> str:
        # TODO: Replace with your handler description
        return "Template for creating a new curl handler"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        # TODO: Define your input parameters schema
        return {
            "type": "object",
            "properties": {
                # Add your parameters here, for example:
                "param1": {
                    "type": "string",
                    "description": "Description of parameter 1 (required)"
                },
                "param2": {
                    "type": "string",
                    "description": "Description of parameter 2 (optional)",
                    "optional": True
                }
            },
            "required": ["param1"],  # List your required parameters
        }
    
    @property
    def timeout(self) -> float:
        """Override timeout if needed"""
        return self.DEFAULT_TIMEOUT
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        # TODO: Validate your required parameters
        param1 = arguments.get("param1")
        if not param1:
            raise ValueError("param1 is required")
            
        # TODO: PASTE YOUR CURL COMMAND HERE
        # Convert your curl command to a list format
        # Example:
        # Original curl command:
        # curl -X POST https://api.example.com/v1/endpoint -H "Authorization: Bearer token" -d '{"key": "value"}'
        #
        # Should be converted to:
        command = [
            "curl",
            "-X", "POST",
            "https://api.example.com/v1/endpoint",
            "-H", "Authorization: Bearer token",
            "-d", '{"key": "value"}'
        ]
        
        # Add timeout for safety
        command.extend(["--max-time", str(self.timeout)])
        
        return command
    
    async def handle(self, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Override this method if you need custom response handling
        For example, if you need to parse JSON responses
        """
        try:
            result = await super().handle(arguments)
            
            # Uncomment and modify if you need JSON parsing:
            # if isinstance(result, (str, bytes)):
            #     try:
            #         return json.loads(result)
            #     except json.JSONDecodeError:
            #         return {"error": "Failed to parse response", "raw": str(result)}
            
            return result
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}",
                "status": "error",
                "details": "The request might have timed out or the service is temporarily unavailable"
            } 