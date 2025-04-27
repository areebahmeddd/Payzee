#!/bin/bash

set -e

echo "Setting up Payzee development environment..."

if ! command -v poetry &> /dev/null; then
    echo "Poetry not found. Installing..."
    powershell -Command "(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -"

    echo "Adding Poetry to PATH..."
    export PATH="$HOME/.poetry/bin:$PATH"
    powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%USERPROFILE%\.poetry\bin', 'User')"

    echo "Poetry installed. Restart terminal after script."
fi

if ! command -v poetry &> /dev/null; then
    echo "Poetry still not found. Update PATH manually."
    exit 1
else
    echo "Poetry ready."
fi

if [ ! -d ".venv" ] || [ ! -f "poetry.lock" ]; then
    echo "Installing dependencies..."
    poetry install --no-root
else
    echo "Dependencies already installed."
fi

echo "Starting server..."
poetry run uvicorn app.app:app --reload
