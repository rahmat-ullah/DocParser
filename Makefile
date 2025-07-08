.PHONY: help install dev test lint format clean

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  dev        - Run development server with uvicorn"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting with ruff"
	@echo "  format     - Format code with black and isort"
	@echo "  clean      - Clean up cache files"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	ruff check app/
	black --check app/
	isort --check-only app/

format:
	black app/
	isort app/
	ruff --fix app/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
