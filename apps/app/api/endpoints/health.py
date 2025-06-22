from fastapi import APIRouter
from ...services.llm_service import LLMService

router = APIRouter()

# Initialize LLM service for health checks
llm_service = LLMService()

@router.get("")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "api_configured": True,
        "llm_services": llm_service.get_health_status(),
        "message": "API is running successfully"
    } 