# Payzee: Pay Easy, Payzee!

**Payzee** is a modern payment processing platform built with **FastAPI**, offering scalable and secure payment solutions with real-time transaction capabilities.

## Setup for New Contributors

### Quick Start

Run the setup script to prepare your development environment:

```bash
./run.sh
```

This script will:

- Install Poetry if it is not already available
- Set up the appropriate PATH variables
- Install project dependencies
- Start the development server with hot-reload enabled

### Pre-commit Hooks

The project uses pre-commit hooks to maintain code quality.  
We use **Ruff** for linting and formatting.

Hooks automatically handle:

- Fixing trailing whitespace
- Ensuring files end with a newline
- Checking JSON and YAML files
- Linting and formatting Python code with Ruff

Pre-commit is installed with the project dependencies.

To run all hooks manually:

```bash
poetry run pre-commit run --all-files
```
