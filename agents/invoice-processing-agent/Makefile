.PHONY: help install test lint format clean run

help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make test     - Run tests"
	@echo "  make lint     - Run linter"
	@echo "  make format   - Format code"
	@echo "  make clean    - Clean up cache files"
	@echo "  make run      - Run the agent"

install:
	pip install -r config/requirements.txt

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/ htmlcov/ .coverage

run:
	python src/invoice_agent.py

setup:
	python3 -m venv venv
	@echo "Virtual environment created!"
	@echo "Activate with: source venv/bin/activate"
	@echo "Then run: make install"
