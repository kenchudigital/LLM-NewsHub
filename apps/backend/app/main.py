from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from .routers import news, dates  # Remove chat import

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="News Portal API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log static directory structure
static_path = Path("../static").resolve()
logger.info(f"Static directory path: {static_path}")
logger.info(f"Static directory exists: {static_path.exists()}")
if static_path.exists():
    logger.info(f"Static directory contents: {list(static_path.iterdir())}")
    images_path = static_path / "images"
    if images_path.exists():
        logger.info(f"Images directory contents: {list(images_path.iterdir())}")

# Add middleware to log static file requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path.startswith("/static"):
        logger.info(f"Static file request: {request.url.path}")
        static_file_path = static_path / request.url.path[8:]  # Remove "/static/" prefix
        logger.info(f"Looking for file at: {static_file_path}")
        logger.info(f"File exists: {static_file_path.exists()}")
    
    response = await call_next(request)
    
    if request.url.path.startswith("/static") and response.status_code != 200:
        logger.warning(f"Static file not found: {request.url.path} (Status: {response.status_code})")
    
    return response

# Mount static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Include routers
app.include_router(news.router, prefix="/api", tags=["news"])
# app.include_router(chat.router, prefix="/api", tags=["chat"])  # Comment out chat router
app.include_router(dates.router, prefix="/api", tags=["dates"])

@app.get("/")
async def root():
    return {"message": "Welcome to the News Portal API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"} 