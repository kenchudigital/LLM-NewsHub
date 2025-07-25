# Makefile for LLM-NewsHub Project
# This Makefile handles setup, installation, and common tasks

.PHONY: help install install-dev setup-nltk clean test run-frontend run-backend run-all

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

# Start frontend application
run-frontend:
	@echo "Starting frontend..."
	cd apps/frontend && npm start

# Start backend API
run-backend:
	@echo "Starting backend API..."
	cd apps && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Full setup (install + setup-nltk)
setup: install setup-nltk
	@echo "Full setup completed!"

# Setup for development
setup-dev: install-dev setup-nltk
	@echo "Development setup completed!"

# Data processing commands
run-all:
	@echo "Running main data processing pipeline..."
	conda run -n llm-news python run_all.py --date "2025-07-22"
	@echo "Running video generation in llm-news-video environment..."
	conda run -n llm-news-video python run_all2.py --date "2025-07-22"
	@echo "Pipeline completed!"

# Model training commands
train-fake-news:
	@echo "Training fake news classifier..."
	cd classifier/fake_news && python run_pipeline.py

train-category:
	@echo "Training category classifier..."
	cd classifier/category && python run_pipeline.py