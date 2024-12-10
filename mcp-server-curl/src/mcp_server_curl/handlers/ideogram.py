import os
import json
from typing import Any, Dict, List, Optional
from . import CurlHandler

class IdeogramGenerateHandler(CurlHandler):
    # 90 seconds timeout for image generation
    DEFAULT_TIMEOUT = 90
    
    @property
    def name(self) -> str:
        return "ideogram-generate"
    
    @property
    def description(self) -> str:
        return "Generate images using Ideogram AI API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt for image generation (required)"
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["ASPECT_10_16"],
                    "default": "ASPECT_10_16",
                    "description": "Image aspect ratio"
                },
                "model": {
                    "type": "string",
                    "enum": ["V_2_TURBO"],
                    "default": "V_2_TURBO",
                    "description": "Model version to use"
                },
                "magic_prompt_option": {
                    "type": "string",
                    "enum": ["AUTO"],
                    "default": "AUTO",
                    "description": "Magic prompt option"
                }
            },
            "required": ["prompt"],
        }
    
    @property
    def timeout(self) -> float:
        """Allow longer timeout for image generation"""
        return self.DEFAULT_TIMEOUT
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        prompt = arguments.get("prompt")
        if not prompt:
            raise ValueError("prompt is required")
            
        api_key = os.getenv("IDEOGRAM_API_KEY")
        if not api_key:
            raise ValueError("IDEOGRAM_API_KEY environment variable is required")
        
        data = {
            "image_request": {
                "prompt": prompt,
                "aspect_ratio": arguments.get("aspect_ratio", "ASPECT_10_16"),
                "model": arguments.get("model", "V_2_TURBO"),
                "magic_prompt_option": arguments.get("magic_prompt_option", "AUTO")
            }
        }
            
        command = [
            "curl",
            "-X", "POST",
            "https://api.ideogram.ai/generate",
            "-H", f"Api-Key: {api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(data)
        ]
        
        return command
    
    async def handle(self, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Override handle method to parse JSON response"""
        try:
            result = await super().handle(arguments)
            
            # Parse the JSON response
            if isinstance(result, (str, bytes)):
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return {"error": "Failed to parse response", "raw": str(result)}
            
            return result
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}",
                "status": "error",
                "details": "The request might have timed out or the service is temporarily unavailable"
            }