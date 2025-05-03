.PHONY: up down restart clean logs test lint format help

help:
	@echo "  make up         Start the Docker containers"
	@echo "  make down       Stop the Docker containers"
	@echo "  make restart    Restart the Docker containers"
	@echo "  make clean      Remove all containers and volumes"
	@echo "  make logs       Stream Docker container logs"
	@echo "  make test       Run tests"
	@echo "  make lint       Run linting with Ruff"
	@echo "  make format     Format code with Ruff"

up:
	@echo "Starting Docker containers..."
	docker-compose up -d

down:
	@echo "Stopping Docker containers..."
	docker-compose down

restart:
	@echo "Restarting Docker containers..."
	docker-compose restart

clean: down
	@echo "Removing all containers, volumes, and images..."
	docker-compose down -v --rmi all --remove-orphans

logs:
	@echo "Streaming logs from Docker containers..."
	docker-compose logs -f

test:
	@echo "Running tests..."
	pytest tests/

lint:
	@echo "Running linting with Ruff..."
	ruff check .

format:
	@echo "Formatting code with Ruff..."
	ruff format .
