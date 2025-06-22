from pydantic import BaseModel
from typing import Optional, List, Dict

class ChatContext(BaseModel):
    currentGroupId: Optional[str] = None
    currentDate: Optional[str] = None
    conversationHistory: List[str] = []

class ChatMessage(BaseModel):
    message: str
    context: Optional[ChatContext] = None

class ChatResponse(BaseModel):
    response: str
    chart_data: Optional[Dict] = None 