from fastapi import APIRouter, HTTPException
from typing import List
import os
from pathlib import Path

router = APIRouter()

@router.get("/dates", response_model=dict)
async def get_available_dates():
    """
    Get a list of available dates from the static directory.
    Returns the latest 7 dates that have article data.
    """
    try:
        # Get the static directory path
        static_dir = Path(__file__).parent.parent.parent / "static"
        articles_dir = static_dir / "articles"
        
        # Get all date directories
        date_dirs = [d.name for d in articles_dir.iterdir() if d.is_dir()]
        
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