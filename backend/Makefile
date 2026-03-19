.PHONY: help install run test lint format clean docker-up docker-down

help:
	@echo "AI Adaptive Onboarding Engine - Makefile Commands"
	@echo "=================================================="
	@echo "make install         - Install dependencies"
	@echo "make run             - Run development server"
	@echo "make run-db          - Run PostgreSQL with Docker"
	@echo "make test            - Run tests"
	@echo "make lint            - Run linter (pylint)"
	@echo "make format          - Format code (black)"
	@echo "make clean           - Clean cache files"
	@echo "make docker-up       - Start Docker containers"
	@echo "make docker-down     - Stop Docker containers"
	@echo "make db-init         - Initialize database"
	@echo "make shell           - Open Python shell"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

run:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-db:
	docker-compose up -d

test:
	pytest tests/ -v --tb=short

lint:
	pylint app/

format:
	black app/
	black tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -delete
	rm -f .coverage
	rm -rf htmlcov/

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-clean:
	docker-compose down -v

db-init:
	python -c "from app.core.database import init_db; init_db(); print('✓ Database initialized')"

shell:
	python

docs:
	@echo "API Documentation: http://localhost:8000/api/v1/docs"
	@echo "ReDoc: http://localhost:8000/api/v1/redoc"

health:
	curl http://localhost:8000/api/v1/health | python -m json.tool

example:
	python examples/test_api.py
