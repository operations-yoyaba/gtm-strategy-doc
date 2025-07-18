.PHONY: help venv install test lint clean deploy local-build docker-build

# Default target
help:
	@echo "Available commands:"
	@echo "  make venv        - Create virtual environment"
	@echo "  make install     - Install dependencies"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting"
	@echo "  make clean       - Clean up generated files"
	@echo "  make local-build - Build locally"
	@echo "  make docker-build- Build Docker image"
	@echo "  make deploy      - Deploy to Cloud Run"

# Create virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  # On Unix/macOS"
	@echo "  venv\\Scripts\\activate     # On Windows"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install pytest black flake8

# Run tests
test:
	pytest -v

# Run linting
lint:
	black --check .
	flake8 .

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .coverage

# Build locally
local-build:
	python -m py_compile main.py
	python -m py_compile models/*.py
	python -m py_compile services/*.py
	python -m py_compile utils/*.py
	@echo "Local build completed successfully"

# Build Docker image
docker-build:
	docker build -t gtm-doc:latest .
	@echo "Docker image built successfully"

# Deploy to Cloud Run
deploy:
	@if [ -z "$(PROJECT_ID)" ]; then \
		echo "Error: PROJECT_ID environment variable not set"; \
		echo "Please set it with: export PROJECT_ID=your-project-id"; \
		exit 1; \
	fi
	./deploy.sh

# Development server
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Format code
format:
	black .

# Security check
security:
	bandit -r .

# Type checking
type-check:
	mypy main.py models/ services/ utils/

# Full check (lint, test, type-check)
check: lint test type-check
	@echo "All checks passed!"

# Install development dependencies
install-dev: install
	pip install pytest-cov bandit mypy black flake8

# Run with coverage
test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

# Clean everything
clean-all: clean
	rm -rf venv
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf .bandit_cache 