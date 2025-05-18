FROM python:3.11-slim AS builder

# ARG APP_HOME=/payzee-api
# ARG BUILD_ENVIRONMENT="production"

ENV POETRY_VERSION=2.1.3 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION" poetry-plugin-export>=1.9.0

COPY pyproject.toml poetry.lock* ./
RUN poetry export -f requirements.txt > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt --target=/dependencies

FROM python:3.11-slim AS runner

WORKDIR /app

COPY --from=builder /dependencies /usr/local/lib/python3.11/site-packages
COPY . .

EXPOSE 8000

# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8002"]
