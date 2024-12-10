import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import mcp.types as types

class CurlHandler(ABC):
    """Base class for all curl handlers"""
    
    # Default timeout in seconds
    DEFAULT_TIMEOUT = 60  # 1 minute
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the handler"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the description of the handler"""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """Return the input schema for the handler"""
        pass
    
    def get_tool_definition(self) -> types.Tool:
        """Get the tool definition for this handler"""
        return types.Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.input_schema
        )
    
    @abstractmethod
    def build_curl_command(self, arguments: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build the curl command for this handler"""
        pass
    
    @property
    def timeout(self) -> float:
        """Return the timeout for this handler in seconds"""
        return self.DEFAULT_TIMEOUT
    
    async def handle(self, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle the curl request"""
        command = self.build_curl_command(arguments)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout
                )
                
                if process.returncode == 0:
                    return {
                        "status": "success",
                        "command": " ".join(command),
                        "output": stdout.decode()
                    }
                else:
                    return {
                        "status": "error",
                        "command": " ".join(command),
                        "error": stderr.decode()
                    }
                    
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except:
                    pass
                return {
                    "status": "timeout",
                    "command": " ".join(command),
                    "error": f"Operation timed out after {self.timeout} seconds"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "command": " ".join(command),
                "error": str(e)
            } 