# Quick Start

```bash
docker-compose -f apps/docker-compose.yml build backend
docker-compose -f apps/docker-compose.yml build frontend
```

After that push the image to Container Registry on the Cloud.


# AI NewsSense - Restructured Backend

This is the restructured backend application following the nexi-dashboard architecture pattern.

## Project Structure

```
new_apps/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Configuration and settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py             # Main API router
│   │   └── endpoints/
│   │       ├── __init__.py
│   │       ├── health.py      # Health check endpoints
│   │       ├── news.py        # News-related endpoints
│   │       └── chat.py        # Chat/AI endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py     # LLM integration service
│   │   ├── news_service.py    # News operations service
│   │   └── chat_service.py    # Chat/conversation service
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── chat.py            # Chat-related Pydantic models
│   │   └── news.py            # News-related Pydantic models
│   └── models/
│       └── __init__.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Key Improvements

### 1. **Modular Architecture**
- Separated concerns into distinct modules (services, schemas, API endpoints)
- Following dependency injection principles
- Clear separation between business logic and API routes

### 2. **Service Layer Pattern**
- `LLMService`: Handles all LLM integrations with fallback mechanisms
- `NewsService`: Manages article loading, caching, and filtering
- `ChatService`: Orchestrates conversations between users and AI

### 3. **Schema Validation**
- Pydantic models for request/response validation
- Type safety throughout the application
- Clear API documentation through schemas

### 4. **Configuration Management**
- Centralized configuration in `core/config.py`
- Environment-based settings
- Easy to modify and extend

## API Endpoints

### Health
- `GET /api/health` - Health check and service status

### News
- `GET /api/news` - Get news articles with filtering
- `GET /api/news/articles/{date}/{group_id}` - Get specific article
- `GET /api/news/categories/{date}` - Get categories for date

### Chat
- `POST /api/chat` - Chat with AI assistant

## Running the Application

### Using Docker Compose (Recommended)
```bash
# From the new_apps directory
docker-compose up -d
```

### Using Python directly
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Environment Variables
The application looks for a `.env` file in the project root directory (LLM-NewsGen/.env):
```
OPENAI_API_KEY=your_openai_key
ALIBABA_LLM_KEY=your_alibaba_key
GEMINI_API_KEY=your_gemini_key
PERPLEXITY_API_KEY=your_perplexity_key
ANTHROPIC_API_KEY=your_anthropic_key
DEBUG=false
```

You can use the provided template:
```bash
# Copy the template to the root directory
cp env_template.txt ../../.env
# Then edit ../../.env with your actual API keys
```

## Benefits of This Structure

1. **Maintainability**: Clear separation of concerns makes the code easier to maintain
2. **Testability**: Each service can be tested independently
3. **Scalability**: Easy to add new features without affecting existing code
4. **Type Safety**: Pydantic schemas ensure data validation
5. **Documentation**: Auto-generated API docs via FastAPI
6. **Performance**: Better caching and memory management
7. **Error Handling**: Centralized error handling and logging

## Migration from Old Structure

The original 535-line `main.py` has been broken down as follows:
- Configuration → `core/config.py`
- LLM clients → `services/llm_service.py`
- News operations → `services/news_service.py`
- Chat logic → `services/chat_service.py`
- API routes → `api/endpoints/`
- Data models → `schemas/`

This structure follows FastAPI best practices and makes the codebase much more maintainable and scalable. 