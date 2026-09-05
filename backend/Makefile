# Makefile for ProjectPulse AI Backend

.PHONY: help run test lint format migrate worker clean

help:
	@echo "Available commands:"
	@echo "  make run       - Run FastAPI server with auto-reload"
	@echo "  make test      - Run automated pytest suite"
	@echo "  make lint      - Check code style"
	@echo "  make migrate   - Apply database migrations"
	@echo "  make clean     - Clean python bytecode and cache"

run:
	uvicorn services.api.main:app --reload --port 8000

test:
	pytest tests/ -v

lint:
	python -m py_compile services/api/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
