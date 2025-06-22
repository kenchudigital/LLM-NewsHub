import os
from openai import OpenAI
from typing import Optional
import json
import sys
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    "read the notebook!"
    
    def __init__(self, publisher: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.publisher = publisher.upper()
        self.api_key = api_key or self._get_default_api_key()
        self.base_url = base_url or self._get_default_base_url()
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=300  # Default 3 minutes timeout for all requests
        )
    
    def _get_default_api_key(self) -> str:
        env_vars = {
            'OPENAI': 'OPENAI_API_KEY',
            'PERPLEXITY': 'PERPLEXITY_API_KEY',
            'ALIBABA': 'ALIBABA_LLM_KEY',
            'GEMINI': 'GEMINI_API_KEY',
        }
        var_name = env_vars.get(self.publisher)
        if not var_name:
            raise ValueError(f"Unsupported publisher: {self.publisher}")
            
        api_key = os.getenv(var_name)
        if not api_key:
            raise ValueError(f"API key not found. Please set {var_name} environment variable or pass it directly.")
        return api_key
    
    def _get_default_base_url(self) -> str:
        urls = {
            'OPENAI': "https://newapi.maxuhe.com/v1",
            'PERPLEXITY': "https://api.perplexity.ai",  
            'ALIBABA': "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            'GEMINI': "https://generativelanguage.googleapis.com/v1beta/",
        }
        return urls.get(self.publisher, "")
    
    def generate(
        self,
        prompt_content: str,
        system_content: str = '你是一個傻瓜Agent',
        temperature: float = 0.5,
        top_p: float = 0.5,
        model: str = 'gpt-4o-mini',  # Default model, adjust as needed
        **kwargs
    ) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=[
                    {'role': 'system', 'content': system_content},
                    {'role': 'user', 'content': prompt_content}
                ],
                temperature=temperature,
                top_p=top_p,
                **kwargs
            )
            return completion
        except Exception as e:
            raise RuntimeError(f"Error generating response from {self.publisher}: {str(e)}")
        
openai_client = LLMClient(publisher='OPENAI')
perplexity_client = LLMClient(publisher='PERPLEXITY')
alibaba_client = LLMClient(publisher='ALIBABA')
gemini_client = LLMClient(publisher='GEMINI')