import aiohttp
import logging
from typing import List, Dict, Optional, Tuple
from ..core.config import settings

# Add dashscope import with error handling
try:
    import dashscope
    from dashscope import Application
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    logging.warning("dashscope library not available. Knowledge Graph features will be disabled.")

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
        self.perplexity_client = None
        self.knowledge_graph_available = False
        self._available_models = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize available LLM clients based on API keys"""
        try:
            if settings.OPENAI_API_KEY:
                self.openai_client = HTTPLLMClient(
                    base_url="https://newapi.maxuhe.com/v1",
                    api_key=settings.OPENAI_API_KEY
                )
                self._available_models["OpenAI"] = [
                    {"name": "GPT-4o Mini", "value": "gpt-4o-mini", "provider": "OpenAI"},
                ]
                logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {e}")

        try:
            if settings.ALIBABA_LLM_KEY:
                self.alibaba_client = HTTPLLMClient(
                    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
                    api_key=settings.ALIBABA_LLM_KEY
                )
                self._available_models["Alibaba"] = [
                    {"name": "Qwen Turbo", "value": "qwen-turbo", "provider": "Alibaba"},
                ]
                logger.info("Alibaba client initialized successfully")
        except Exception as e:
            logger.warning(f"Alibaba client initialization failed: {e}")

        try:
            if settings.GEMINI_API_KEY:
                self.gemini_client = HTTPLLMClient(
                    base_url="https://generativelanguage.googleapis.com/v1beta",
                    api_key=settings.GEMINI_API_KEY
                )
                self._available_models["Gemini"] = [
                    {"name": "Gemini 1.5 Flash", "value": "gemini-1.5-flash", "provider": "Gemini"},
                ]
                logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.warning(f"Gemini client initialization failed: {e}")
        
        try:
            if settings.PERPLEXITY_API_KEY:
                self.perplexity_client = HTTPLLMClient(
                    base_url="https://api.perplexity.ai",
                    api_key=settings.PERPLEXITY_API_KEY
                )
                self._available_models["Perplexity"] = [
                    {"name": "Sonar", "value": "llama-3.1-sonar-small-128k-online", "provider": "Perplexity"},
                ]
                logger.info("Perplexity client initialized successfully")
        except Exception as e:
            logger.warning(f"Perplexity client initialization failed: {e}")
        
        # Initialize Knowledge Graph availability
        if DASHSCOPE_AVAILABLE and hasattr(settings, 'ALIBABA_LLM_KEY_KG') and settings.ALIBABA_LLM_KEY_KG:
            self.knowledge_graph_available = True
            logger.info("Knowledge Graph service available")
        else:
            logger.warning("Knowledge Graph service not available - missing dashscope library or API key")
    
    def get_available_models(self) -> List[Dict]:
        """Get list of all available models grouped by provider"""
        all_models = []
        
        # Add models from each provider
        for provider, models in self._available_models.items():
            all_models.extend(models)
        
        # Always add Knowledge Graph option (even if not configured, for UI consistency)
        all_models.append({
            "name": "Knowledge Graph", 
            "value": "knowledge-graph", 
            "provider": "Knowledge"
        })
        
        # If no API keys are configured, provide fallback models for UI
        if not all_models or len(all_models) == 1:  # Only Knowledge Graph
            fallback_models = [
                {"name": "GPT-4o Mini", "value": "gpt-4o-mini", "provider": "OpenAI"},
                {"name": "Qwen Turbo", "value": "qwen-turbo", "provider": "Alibaba"},
                {"name": "Gemini 1.5 Flash", "value": "gemini-1.5-flash", "provider": "Gemini"},
                {"name": "Perplexity", "value": "llama-3.1-sonar-small-128k-online", "provider": "Perplexity"},
                {"name": "Knowledge Graph", "value": "knowledge-graph", "provider": "Knowledge"}
            ]
            return fallback_models
        
        return all_models
    
    def get_default_model(self) -> Dict:
        """Get the default model"""
        all_models = self.get_available_models()
        if all_models:
            # Return GPT-4o Mini as default if available
            for model in all_models:
                if model["value"] == "gpt-4o-mini":
                    return model
            # Otherwise return first available model (excluding knowledge graph)
            for model in all_models:
                if model["value"] != "knowledge-graph":
                    return model
        return {"name": "GPT-4o Mini", "value": "gpt-4o-mini", "provider": "OpenAI"}
    
    async def _call_knowledge_graph(self, user_query: str, article_context: str = "") -> Dict[str, str]:
        """Call Alibaba Cloud Knowledge Graph via DashScope Application API"""
        if not self.knowledge_graph_available:
            return {
                "response": "🔍 Knowledge Graph service is not available. Please contact the administrator to configure the service.",
                "provider": "Knowledge Graph",
                "model": "knowledge-graph"
            }
        
        try:
            # Set the API base URL
            dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
            
            # Use the user query directly as the prompt
            kg_prompt = user_query
            
            # Call the Knowledge Graph Application
            response = Application.call(
                api_key=settings.ALIBABA_LLM_KEY_KG,
                app_id='b0534f9cd7334c6e8cb8b866fd34ea9f',
                prompt=kg_prompt,
                parameters={
                    "temperature": 0.8,
                    "max_tokens": 1024
                }
            )
            
            # Handle response as dict (dashscope returns dict, not object)
            if response and isinstance(response, dict):
                # Check if response contains output
                if 'output' in response and 'text' in response['output']:
                    kg_response = response['output']['text']
                    logger.info("Knowledge Graph analysis completed successfully")
                    
                    return {
                        "response": kg_response,
                        "provider": "Alibaba Knowledge Graph",
                        "model": "knowledge-graph"
                    }
                else:
                    # Log the response structure for debugging
                    logger.error(f"Unexpected response structure from Knowledge Graph API: {response}")
                    return {
                        "response": f"🔍 Knowledge Graph analysis completed, but the response format was unexpected. Response: {response}",
                        "provider": "Alibaba Knowledge Graph",
                        "model": "knowledge-graph"
                    }
            else:
                logger.error(f"Invalid response format from Knowledge Graph API: {type(response)}")
                return {
                    "response": "🔍 Knowledge Graph analysis completed, but the response format was unexpected. Please try again.",
                    "provider": "Alibaba Knowledge Graph",
                    "model": "knowledge-graph"
                }
                
        except Exception as e:
            logger.error(f"Error calling Knowledge Graph API: {str(e)}")
            return {
                "response": f"🔍 **Knowledge Graph Analysis Error:**\n\nI encountered an issue while analyzing the content: {str(e)}\n\nPlease try again later or contact support if the problem persists.",
                "provider": "Alibaba Knowledge Graph",
                "model": "knowledge-graph"
            }
    
    async def get_response(self, messages: List[Dict], preferred_model: Optional[str] = None) -> Dict[str, str]:
        """Get response using specified model or fallback to available models"""
        
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
        
        # Handle knowledge graph request
        if preferred_model == "knowledge-graph":
            return await self._call_knowledge_graph(current_message, system_message)
        
        # Try to use preferred model first
        if preferred_model:
            client_info = self._get_client_for_model(preferred_model)
            if client_info:
                try:
                    client_name, client, model = client_info
                    logger.info(f"Using preferred model: {model} from {client_name}")
                    
                    response = await client.generate(
                        prompt_content=full_prompt,
                        system_content=system_message,
                        temperature=0.7,
                        model=model
                    )
                    
                    if "choices" in response and response["choices"]:
                        content = response["choices"][0]["message"]["content"]
                        logger.info(f"Successfully got response from preferred model {model}")
                        return {
                            "response": content,
                            "provider": client_name,
                            "model": model
                        }
                except Exception as e:
                    logger.error(f"Error with preferred model {preferred_model}: {str(e)}")
        
        # Fallback to available clients if preferred model fails
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
                logger.info(f"Trying fallback {client_name} API...")
                
                response = await client.generate(
                    prompt_content=full_prompt,
                    system_content=system_message,
                    temperature=0.7,
                    model=model
                )
                
                if "choices" in response and response["choices"]:
                    content = response["choices"][0]["message"]["content"]
                    logger.info(f"Successfully got response from fallback {client_name}")
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
    
    def _get_client_for_model(self, model_value: str) -> Optional[Tuple[str, HTTPLLMClient, str]]:
        """Get client and model info for a specific model value"""
        # Check OpenAI models
        if self.openai_client:
            openai_models = ["gpt-4o-mini"]
            if model_value in openai_models:
                return ("OpenAI", self.openai_client, model_value)
        
        # Check Alibaba models
        if self.alibaba_client:
            alibaba_models = ["qwen-turbo"]
            if model_value in alibaba_models:
                return ("Alibaba", self.alibaba_client, model_value)
        
        # Check Gemini models
        if self.gemini_client:
            gemini_models = ["gemini-1.5-flash"]
            if model_value in gemini_models:
                return ("Gemini", self.gemini_client, model_value)
        
        # Check Perplexity models
        if self.perplexity_client:
            perplexity_models = ["llama-3.1-sonar-small-128k-online"]
            if model_value in perplexity_models:
                return ("Perplexity", self.perplexity_client, model_value)
        
        return None
    
    def _get_available_clients(self) -> List[Tuple[str, HTTPLLMClient, str]]:
        """Get list of available clients with their default configurations"""
        clients = []
        
        if self.openai_client:
            clients.append(("OpenAI", self.openai_client, "gpt-4o-mini"))
        if self.alibaba_client:
            clients.append(("Alibaba", self.alibaba_client, "qwen-turbo"))
        if self.gemini_client:
            clients.append(("Gemini", self.gemini_client, "gemini-1.5-flash"))
        if self.perplexity_client:
            clients.append(("Perplexity", self.perplexity_client, "llama-3.1-sonar-small-128k-online"))
        
        return clients
    
    def get_health_status(self) -> Dict[str, bool]:
        """Get health status of all LLM services"""
        return {
            "openai": bool(self.openai_client),
            "perplexity": bool(self.perplexity_client),
            "anthropic": bool(settings.ANTHROPIC_API_KEY),
            "alibaba": bool(self.alibaba_client),
            "gemini": bool(self.gemini_client),
            "knowledge_graph": self.knowledge_graph_available
        } 