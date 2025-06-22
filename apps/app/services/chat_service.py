import logging
from typing import Dict, List, Optional
from ..schemas.chat import ChatMessage, ChatContext, ChatResponse
from .llm_service import LLMService
from .news_service import NewsService

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, llm_service: LLMService, news_service: NewsService):
        self.llm_service = llm_service
        self.news_service = news_service
        self.conversation_memory: Dict[str, List[Dict]] = {}
    
    def create_system_prompt(self, article_context: str, rag_context: str) -> str:
        """Create an enhanced system prompt for the AI assistant"""
        
        base_prompt = """You are an AI news assistant for AI NewsSense, an advanced news analysis platform. You have access to comprehensive news data including articles, social media posts, comments, and detailed publisher information.

CAPABILITIES:
1. 📰 Article Analysis: Provide summaries, explain key points, analyze sentiment and credibility
2. 🔍 Source Verification: Help users understand publisher credibility, bias, and regional diversity  
3. 📊 Data Insights: Analyze metrics like sentiment scores, fake news probability, engagement patterns
4. 🌍 Context Awareness: Use article context, social media data, and conversation history
5. 📈 Trend Analysis: Identify patterns across publishers, regions, and time

RESPONSE STYLE:
- Be conversational, helpful, and analytical
- Provide evidence-based insights using the available data
- Cite specific metrics when relevant (sentiment scores, credibility ratings, etc.)
- Explain publisher diversity and geographic coverage
- Be transparent about data limitations
- Use emojis sparingly for better readability

AVAILABLE DATA INCLUDES:
- Full article content with section-by-section analysis
- Publisher credibility scores and bias ratings
- Regional diversity of sources
- Social media posts and public sentiment
- Fake news probability scores
- Engagement metrics and comment analysis"""

        if article_context:
            base_prompt += f"\n\n📋 CURRENT ARTICLE DATA:\n{article_context}"
        
        if rag_context:
            base_prompt += f"\n\n📚 ADDITIONAL RESEARCH DATA:\n{rag_context}"
        
        base_prompt += """

💡 INSTRUCTIONS:
- Always reference specific data points when making claims
- Explain methodology behind credibility and sentiment scores
- Highlight publisher diversity and potential bias
- Provide actionable insights for news consumers
- If asked about charts or visualizations, describe what would be shown but note that chart generation is currently limited"""
        
        return base_prompt
    
    async def process_chat_message(self, message: ChatMessage) -> ChatResponse:
        """Process a chat message and return AI response"""
        try:
            user_message = message.message.strip()
            context = message.context
            
            if not user_message:
                return ChatResponse(
                    response="Please provide a message to chat with me.",
                    chart_data=None
                )
            
            # Build context for AI response
            current_date = context.currentDate if context and context.currentDate else "2025-06-14"
            current_group_id = context.currentGroupId if context and context.currentGroupId else None
            
            # Get conversation history
            session_id = f"{current_group_id}_{current_date}" if current_group_id else "general"
            if session_id not in self.conversation_memory:
                self.conversation_memory[session_id] = []
            
            # Get article and RAG context
            article_context = ""
            rag_context = ""
            
            if current_group_id and current_date:
                article_context = self.news_service.get_article_context(current_group_id, current_date)
                rag_context = self.news_service.get_rag_context(current_group_id, current_date, user_message)
            
            # Create system prompt
            system_prompt = self.create_system_prompt(article_context, rag_context)
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history in chronological order
            for msg in self.conversation_memory[session_id][-3:]:  # Last 3 exchanges
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})

            # Add current user message last
            messages.append({"role": "user", "content": user_message})
            
            # Get LLM response
            llm_response = await self.llm_service.get_response(messages)
            ai_response = llm_response.get("response", "I'm sorry, I couldn't process your request.")
            
            # Store conversation in memory
            self.conversation_memory[session_id].append({
                "user": user_message,
                "assistant": ai_response
            })
            
            # Keep only last 10 exchanges to prevent memory bloat
            if len(self.conversation_memory[session_id]) > 10:
                self.conversation_memory[session_id] = self.conversation_memory[session_id][-10:]
            
            logger.info(f"Chat processed successfully for session {session_id}")
            
            return ChatResponse(
                response=ai_response,
                chart_data=None  # Chart functionality removed for simplicity
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            return ChatResponse(
                response="I'm sorry, but I encountered an error while processing your request. Please try again.",
                chart_data=None
            ) 