# Makefile for LLM-NewsHub Project
# This Makefile handles setup, installation, and common tasks

.PHONY: help install install-dev setup-nltk clean test run-frontend run-backend run-all

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  setup-nltk   - Download required NLTK data (fixes Resource not found errors)"
	@echo "  clean        - Clean up cache and temporary files"
	@echo "  test         - Run tests"
	@echo "  run-frontend - Start the frontend application"
	@echo "  run-backend  - Start the backend API"
	@echo "  run-all      - Start both frontend and backend"

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	pip install -r requirements-adjusted.txt
	@echo "Dependencies installed successfully!"

# Install development dependencies
install-dev: install
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov black flake8 mypy
	@echo "Development dependencies installed!"

# Setup NLTK data (fixes Resource not found errors)
setup-nltk:
	@echo "Setting up NLTK data..."
	python setup_nltk.py
	@echo "NLTK setup completed!"

# Alternative NLTK setup using direct Python commands
setup-nltk-alt:
	@echo "Setting up NLTK data (alternative method)..."
	python -c "import nltk; import ssl; ssl._create_default_https_context = ssl._create_unverified_context; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('vader_lexicon'); nltk.download('averaged_perceptron_tagger'); print('NLTK data downloaded successfully!')"
	@echo "NLTK setup completed!"

# Clean up cache and temporary files
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "Cleanup completed!"

# Run tests
test:
	@echo "Running tests..."
	python -m pytest tests/ -v --cov=.

# Start frontend application
run-frontend:
	@echo "Starting frontend..."
	cd apps/frontend && npm start

# Start backend API
run-backend:
	@echo "Starting backend API..."
	cd apps && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start both frontend and backend (requires tmux or similar)
run-all:
	@echo "Starting both frontend and backend..."
	@echo "Note: This requires tmux. Install with: brew install tmux (macOS) or apt-get install tmux (Ubuntu)"
	tmux new-session -d -s llm-newshub
	tmux split-window -h -t llm-newshub
	tmux send-keys -t llm-newshub:0.0 "make run-backend" Enter
	tmux send-keys -t llm-newshub:0.1 "make run-frontend" Enter
	tmux attach-session -t llm-newshub

# Full setup (install + setup-nltk)
setup: install setup-nltk
	@echo "Full setup completed!"

# Setup for development
setup-dev: install-dev setup-nltk
	@echo "Development setup completed!"

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t llm-newshub .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 -p 3000:3000 llm-newshub

# Data processing commands
process-data:
	@echo "Processing data..."
	python run_all.py

# Model training commands
train-fake-news:
	@echo "Training fake news classifier..."
	cd classifier/fake_news && python run_pipeline.py

train-category:
	@echo "Training category classifier..."
	cd classifier/category && python run_pipeline.py

# Debug NLTK issues
debug-nltk:
	@echo "Debugging NLTK installation..."
	python -c "import nltk; print('NLTK version:', nltk.__version__); print('NLTK data path:', nltk.data.path)"
	@echo "Checking punkt tokenizer..."
	python -c "from nltk.tokenize import word_tokenize; print('Punkt tokenizer test:', word_tokenize('Hello world!'))" 