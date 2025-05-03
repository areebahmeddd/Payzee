import redis
import os

# Load environment variables for Redis configuration
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_db = int(os.environ.get("REDIS_DB", 0))

# Initialize Redis client
redis_client = redis.Redis(
    host=redis_host, port=redis_port, db=redis_db, decode_responses=True
)

# Collection prefixes for different entity types
CITIZENS_PREFIX = "citizens:"
VENDORS_PREFIX = "vendors:"
GOVERNMENTS_PREFIX = "governments:"
SCHEMES_PREFIX = "schemes:"
TRANSACTIONS_PREFIX = "transactions:"

# Index sets to track all entities of each type
CITIZENS_SET = "citizens_set"
VENDORS_SET = "vendors_set"
GOVERNMENTS_SET = "governments_set"
SCHEMES_SET = "schemes_set"
TRANSACTIONS_SET = "transactions_set"
