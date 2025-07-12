from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ...services.news_service import NewsService
from ...core.config import settings
from pathlib import Path

router = APIRouter()

# Initialize news service
news_service = NewsService()

@router.get("")
async def get_news(
    category: Optional[str] = None,
    search: Optional[str] = None,
    date: Optional[str] = None,
    fuzzy: bool = Query(False, description="Enable fuzzy search")  # Add fuzzy parameter
):
    """Get news articles with optional filtering"""
    try:
        # Use most recent date if no date specified
        if not date:
            date = news_service.get_most_recent_date()
        
        return news_service.get_filtered_news(date, category, search, fuzzy)  # Pass fuzzy parameter
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch news")

@router.get("/articles/{date}/{group_id}")
async def get_article(date: str, group_id: str):
    """Get a specific article by date and group ID"""
    try:
        article = news_service.get_article(date, group_id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        return article
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch article")

@router.get("/categories")
async def get_categories():
    """Get all available news categories"""
    try:
        # Get the most recent date from available data
        static_dir = Path("static/articles")
        if not static_dir.exists():
            return {"categories": {
                "social": "social",
                "entertainment": "entertainment", 
                "tech": "tech",
                "sport": "sport"
            }, "total": 4}
        
        # Find the most recent date directory
        date_dirs = [d for d in static_dir.iterdir() if d.is_dir()]
        if not date_dirs:
            return {"categories": {
                "social": "social",
                "entertainment": "entertainment",
                "tech": "tech", 
                "sport": "sport"
            }, "total": 4}
        
        latest_date = max(date_dirs, key=lambda x: x.name)
        return news_service.get_categories(latest_date.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.get("/categories/{date}")
async def get_categories_by_date(date: str):
    """Get categories for a specific date"""
    try:
        return news_service.get_categories(date)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.get("/dates")
async def get_available_dates():
    """Get available dates from the static directory"""
    try:
        static_dir = Path("static/articles")
        if not static_dir.exists():
            return {"dates": [], "total": 0}
        
        # Get all date directories
        date_dirs = [d.name for d in static_dir.iterdir() if d.is_dir()]
        
        # Sort dates in descending order (newest first)
        sorted_dates = sorted(date_dirs, reverse=True)
        
        # Take the latest 7 dates
        latest_dates = sorted_dates[:7]
        
        return {
            "dates": latest_dates,
            "total": len(latest_dates)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching available dates: {str(e)}"
        ) 