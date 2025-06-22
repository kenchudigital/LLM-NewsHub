from fastapi import APIRouter, HTTPException
from ...schemas.chat import ChatMessage, ChatResponse
from ...services.chat_service import ChatService
from ...services.llm_service import LLMService
from ...services.news_service import NewsService

router = APIRouter()

# Initialize services
llm_service = LLMService()
news_service = NewsService()
chat_service = ChatService(llm_service, news_service)

@router.post("")
async def chat_with_ai(message: ChatMessage) -> ChatResponse:
    """Chat with AI assistant"""
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = await chat_service.process_chat_message(message)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to process chat message")
 