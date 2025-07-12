from fastapi import APIRouter
from ...core.config import settings

router = APIRouter()

@router.get("/summary-date")
async def get_summary_date():
    """Get the summary video date from configuration"""
    return {
        "date": settings.SUMMARY_DATE,
        "formatted_date": settings.SUMMARY_DATE
    }

@router.get("")
async def get_config():
    """Get application configuration"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.VERSION,
        "summary_date": settings.SUMMARY_DATE,
        "default_news_date": settings.DEFAULT_NEWS_DATE
    } 