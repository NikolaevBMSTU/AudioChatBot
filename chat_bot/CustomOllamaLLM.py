import os
from typing import Dict, Any
from pydantic import BaseModel
from langchain.llms.base import LLM
from requests.auth import HTTPBasicAuth
import requests


class CustomLLMConfig(BaseModel):
    """Configuration schema for our custom Ollama model."""
    api_url: str
    username: str
    password: str


class CustomOllamaLLM(LLM):
    """Custom LLM class for interacting with a remote Ollama instance over HTTP with basic auth."""
    
    config: CustomLLMConfig

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"api_url": self.config.api_url}
    
    def _llm_type(self) -> str:
        return "custom_ollama_llm"

    def _call(self, prompt: str, stop: list = None) -> str:
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'llama3.2',
            'stream': False,
            'prompt': prompt
        }
        
        # Make authenticated request to Ollama API endpoint
        response = requests.post(
            f"{self.config.api_url}/generate",
            json=data,
            auth=HTTPBasicAuth(self.config.username, self.config.password),
            headers=headers
        )

        if response.status_code != 200:
            raise ValueError(f"API returned error {response.status_code}: {response.text}. Posted {data}")
        
        result = response.json()
        return result.get('response', '')
