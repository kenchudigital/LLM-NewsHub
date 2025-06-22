from pydantic import BaseModel
from typing import Optional

class NewsArticle(BaseModel):
    id: int
    headline: str
    category: str
    content: str
    summary: str
    date: str
    image_url: Optional[str] = None 