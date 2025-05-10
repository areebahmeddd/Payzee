# Payzee: Pay Easy, Payzee!

**Payzee** is a modern payment processor powered by **Central Bank Digital Currency (CBDC)** — also known as the **Digital Rupee** or **e-rupee (e₹)**.

## 📁 Project Structure

```
├── app.py             # Main FastAPI application entry point
├── .devcontainer/     # Development container configuration
├── .github/           # GitHub workflows and configuration
├── db/                # Redis database configuration and operations
├── docker/            # Docker configuration files
├── docs/              # Documentation files
├── middleware/        # Request/response middleware components
├── models/            # Data models for transactions, users, and payment entities
├── routes/            # API endpoints for payments and authentication
├── scripts/           # Development and setup scripts
├── templates/         # HTML templates for the application
├── tests/             # Unit and integration tests
└── utils/             # Helper utilities and common functions
```

## 🚀 Setup for Development

### Prerequisites

- Python 3.11+
- Redis server
- [Poetry](https://python-poetry.org) for dependency management

### ⚡ Quick Start

Run the setup script:

```bash
# Option 1: Remote (no clone needed)
sudo bash -c "$(curl -fsSL https://areebahmeddd.github.io/payzee/install.sh)"

# Option 2: Local (after cloning)
./scripts/install.sh
```

Both install dependencies and start the dev server.

This script will:

- Install Poetry (if not already installed)
- Set up necessary `PATH` variables
- Install project dependencies
- Start the development server with hot-reload

## 🐳 Docker Setup (Recommended)

### 1. Start the full stack

Using Docker Compose:

```bash
docker-compose up -d
```

Or with Make:

```bash
make up
```

To view logs from all services:

```bash
docker-compose logs -f
```

To view logs for a specific service (e.g., `api`):

```bash
docker-compose logs -f api
```

### 2. Run the app manually with Docker

```bash
# Build the API container
docker build -t payzee-api -f docker/dev.Dockerfile .

# Run the API container
docker run -p 8000:8000 --env-file .env payzee-api
```

## 🧰 Manual Setup

### 1. Install Poetry

- **Windows**:

  ```bash
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
  ```

- **Linux/macOS**:

  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

### 2. Start Redis using Docker

```bash
docker run --name payzee-redis -p 6379:6379 -d redis:latest
```

### 3. Install project dependencies

```bash
poetry install
```

### 4. Start the development server

```bash
poetry run uvicorn app:app --reload
```

## 🧪 Development Tools

### ✅ Testing

Run tests with `pytest`:

```bash
# Using poetry
poetry run pytest

# Or with Make
make test
```

### 🧼 Pre-commit Hooks

We use **pre-commit** hooks with **Ruff** for linting and formatting.

Hooks handle:

- Removing trailing whitespace
- Ensuring files end with a newline
- Checking JSON/YAML syntax
- Python linting & formatting with Ruff

Pre-commit is installed with project dependencies.

To run all hooks manually:

```bash
poetry run pre-commit run --all-files
```

Or use Make:

```bash
make lint     # Run Ruff linting
make format   # Format code using Ruff
```

## 🔌 Redis Management

RedisInsight is available via Docker at:
👉 [http://localhost:5540](http://localhost:5540)

To connect:

1. Click **Add Redis database**
2. Use one of the following connection strings:

   - `redis://localhost:6379`
   - `redis://host.docker.internal:6379`

This allows inspection of Redis data and keyspaces.

## 📘 API Documentation

Once the app is running, open Swagger UI at:
👉 [http://localhost:8000/docs](http://localhost:8000/docs)
