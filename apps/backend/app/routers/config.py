from fastapi import APIRouter
from pathlib import Path
import os

router = APIRouter()

@router.get("/summary-date")
async def get_summary_date():
    """Get the summary video date from configuration"""
    # 从环境变量或默认值获取
    summary_date = os.getenv('SUMMARY_DATE', '2025-07-12')
    
    return {
        "date": summary_date,
        "formatted_date": summary_date
    }

@router.get("")
async def get_config():
    """Get application configuration"""
    summary_date = os.getenv('SUMMARY_DATE', '2025-07-12')
    
    return {
        "app_name": "AI NewsSense",
        "version": "1.0.0",
        "summary_date": summary_date,
        "default_news_date": "2025-06-14"
    } 