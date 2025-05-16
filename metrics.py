from prometheus_client import Counter, Histogram, Summary

# API request metrics
API_REQUESTS = Counter(
    "api_requests_total",
    "Total count of API requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Request latency in seconds", ["method", "endpoint"]
)

# HTTP request metrics (used in middleware)
HTTP_REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests count",
    ["method", "endpoint", "http_status"],
)

HTTP_REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

# Database metrics
DB_QUERY_TIME = Summary(
    "db_query_processing_seconds", "Time spent processing database queries"
)

REDIS_QUERY_TIME = Summary(
    "redis_query_processing_seconds",
    "Time spent processing Redis database queries",
    ["operation", "collection"],
)


# Helper functions
def increment_request_count(method, endpoint, status_code):
    """Increment the request counter for the given parameters."""
    API_REQUESTS.labels(method=method, endpoint=endpoint, status_code=status_code).inc()


def observe_request_latency(method, endpoint, duration):
    """Record the latency of a request."""
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)


def observe_db_query_time(duration):
    """Record the time spent on a database query."""
    DB_QUERY_TIME.observe(duration)


def observe_redis_query_time(operation, collection, duration):
    """Record the time spent on a Redis database query."""
    REDIS_QUERY_TIME.labels(operation=operation, collection=collection).observe(
        duration
    )
