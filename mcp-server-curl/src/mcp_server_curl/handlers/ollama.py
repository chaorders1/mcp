import os
import json
from typing import Any, Dict, List, Optional
from . import CurlHandler

class OllamaGenerateHandler(CurlHandler):
    @property
    def name(self) -> str:
        return "ollama-generate"
    
    @property
    def description(self) -> str:
        return "Generate text using Ollama API"
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "default": "llama3.2:latest",
                    "description": "The model to use for text generation (default: llama3.2:latest)"
                },
                "prompt": {
                    "type": "string",
                    "description": "The input text prompt for generation (required)"
                },
                "temperature": {
                    "type": "number",
                    "optional": True,
                    "default": 0.7,
                    "description": "Controls randomness in generation (0.0-1.0, default: 0.7)"
                },
                "stream": {
                    "type": "boolean",
                    "optional": True,
                    "default": False,
                    "description": "Whether to stream the response (default: false)"
                },
            },
            "required": ["prompt"],
        }
    
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        if not arguments:
            raise ValueError("Arguments are required")
            
        prompt = arguments.get("prompt")
        if not prompt:
            raise ValueError("prompt is required")
            
        model = arguments.get("model", "llama3.2:latest")
        base_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
        url = f"{base_url}/api/generate"
        
        data = {
            "model": model,
            "prompt": prompt,
            "temperature": arguments.get("temperature", 0.7),
            "stream": arguments.get("stream", False)
        }
        
        return [
            "curl",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "--fail-with-body",
            "-d", json.dumps(data),
            url
        ] 