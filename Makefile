.PHONY: up down restart clean logs seed test lint format

up:
	@echo "Starting Docker containers..."
	docker compose up -d

down:
	@echo "Stopping Docker containers..."
	docker compose down

restart:
	@echo "Restarting Docker containers..."
	docker compose restart

clean: down
	@echo "Removing all containers, volumes, and images..."
	docker compose down -v --rmi all --remove-orphans

logs:
	@echo "Streaming logs from Docker containers..."
	docker compose logs -f

seed:
	@echo "Seeding database with test data..."
	bash scripts/seed_data.sh

test:
	@echo "Running tests..."
	pytest tests/ -v

lint:
	@echo "Running linting with Ruff..."
	ruff check .

format:
	@echo "Formatting code with Ruff..."
	ruff format .
