import aiohttp
import logging
from typing import List, Dict, Optional, Tuple
from ..core.config import settings

logger = logging.getLogger(__name__)

class HTTPLLMClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
    
    async def generate(self, prompt_content: str, system_content: str, temperature: float = 0.7, model: str = "gpt-4o-mini"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt_content}
            ],
            "temperature": temperature,
            "max_tokens": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"API error {response.status}: {error_text}")

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.alibaba_client = None
        self.gemini_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients based on API keys"""
        try:
            if settings.OPENAI_API_KEY:
                self.openai_client = HTTPLLMClient(
                    base_url="https://newapi.maxuhe.com/v1",
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}")

        try:
            if settings.ALIBABA_LLM_KEY:
                self.alibaba_client = HTTPLLMClient(
                    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                    api_key=settings.ALIBABA_LLM_KEY
                )
                logger.info("Alibaba client initialized successfully")
        except Exception as e:
            logger.warning(f"Alibaba client initialization failed: {e}")

        try:
            if settings.GEMINI_API_KEY:
                self.gemini_client = HTTPLLMClient(
                    base_url="https://generativelanguage.googleapis.com/v1beta",
                    api_key=settings.GEMINI_API_KEY
                )
                logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.warning(f"Gemini client initialization failed: {e}")
    
    async def get_response(self, messages: List[Dict]) -> Dict[str, str]:
        """Get response using available LLM clients with fallback"""
        
        # Extract system message and conversation
        system_message = ""
        conversation_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append(msg)
        
        # Build conversation history for context
        conversation_context = ""
        if len(conversation_messages) > 1:
            for msg in conversation_messages[:-1]:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation_context += f"{role}: {msg['content']}\n"
        
        # Get current user message
        current_message = conversation_messages[-1]["content"] if conversation_messages else ""
        
        # Add conversation context to current message if exists
        if conversation_context:
            full_prompt = f"Previous conversation:\n{conversation_context}\nCurrent question: {current_message}"
        else:
            full_prompt = current_message
        
        # Try different clients in order of preference
        clients_to_try = self._get_available_clients()
        
        if not clients_to_try:
            logger.error("No LLM clients available")
            return {
                "response": "I'm sorry, but no AI services are currently configured. Please contact the administrator.",
                "provider": "None",
                "model": "None"
            }
        
        for client_name, client, model in clients_to_try:
            try:
                logger.info(f"Trying {client_name} API...")
                
                response = await client.generate(
                    prompt_content=full_prompt,
                    system_content=system_message,
                    temperature=0.7,
                    model=model
                )
                
                if "choices" in response and response["choices"]:
                    content = response["choices"][0]["message"]["content"]
                    logger.info(f"Successfully got response from {client_name}")
                    return {
                        "response": content,
                        "provider": client_name,
                        "model": model
                    }
                    
            except Exception as e:
                logger.error(f"Error with {client_name}: {str(e)}")
                continue
        
        return {
            "response": "I'm sorry, but I'm having trouble connecting to the AI services right now. Please try again later.",
            "provider": "None",
            "model": "None"
        }
    
    def _get_available_clients(self) -> List[Tuple[str, HTTPLLMClient, str]]:
        """Get list of available clients with their configurations"""
        clients = []
        
        if self.openai_client:
            clients.append(("OpenAI", self.openai_client, "gpt-4o-mini"))
        if self.alibaba_client:
            clients.append(("Alibaba", self.alibaba_client, "qwen-plus"))
        if self.gemini_client:
            clients.append(("Gemini", self.gemini_client, "gemini-1.5-flash"))
        
        return clients
    
    def get_health_status(self) -> Dict[str, bool]:
        """Get health status of all LLM services"""
        return {
            "openai": bool(self.openai_client),
            "perplexity": bool(settings.PERPLEXITY_API_KEY),
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "alibaba": bool(self.alibaba_client),
            "gemini": bool(self.gemini_client)
        } 