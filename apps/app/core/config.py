import os
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from root directory
root_dir = Path(__file__).resolve().parent.parent.parent.parent
env_path = root_dir / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    # API Configuration
    APP_NAME: str = "AI NewsSense API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM API Keys
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    PERPLEXITY_API_KEY: str = os.getenv('PERPLEXITY_API_KEY', '')
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    ALIBABA_LLM_KEY: str = os.getenv('ALIBABA_LLM_KEY', '')
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    
    # CORS Configuration
    ALLOWED_ORIGINS: list = ["*"]  # In production, replace with specific origins
    
    # Cache Configuration
    CACHE_TTL: int = 3600  # 1 hour
    
    # Default date for news - will be overridden by most recent available date
    DEFAULT_NEWS_DATE: str = "2025-06-14"
    
    @property
    def get_default_news_date(self) -> str:
        """Get the most recent available date dynamically"""
        static_dir = Path("static/articles")
        if not static_dir.exists():
            return self.DEFAULT_NEWS_DATE
        
        date_dirs = [d.name for d in static_dir.iterdir() if d.is_dir()]
        if not date_dirs:
            return self.DEFAULT_NEWS_DATE
        
        return max(date_dirs)

settings = Settings() 