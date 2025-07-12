from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatContext(BaseModel):
    currentGroupId: Optional[str] = None
    currentDate: Optional[str] = None
    conversationHistory: Optional[List[str]] = None

class ChatMessage(BaseModel):
    message: str
    context: Optional[ChatContext] = None
    model: Optional[str] = None  # Add model selection

class ChatResponse(BaseModel):
    response: str
    chart_data: Optional[Dict[str, Any]] = None
    model_used: Optional[str] = None  # Add model info to response
    provider_used: Optional[str] = None  # Add provider info to response 