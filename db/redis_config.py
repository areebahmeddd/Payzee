import redis
import os

redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))
redis_db = int(os.environ.get("REDIS_DB", 0))

# Initialize Redis client
redis_client = redis.Redis(
    host=redis_host, port=redis_port, db=redis_db, decode_responses=True
)

# Collection prefixes for different entity types
CITIZENS_PREFIX = "citizen:"
VENDORS_PREFIX = "vendor:"
GOVERNMENTS_PREFIX = "govt:"
SCHEMES_PREFIX = "scheme:"
TRANSACTIONS_PREFIX = "txn:"

# Index sets to track all entities of each type
CITIZENS_SET = "citizens"
VENDORS_SET = "vendors"
GOVERNMENTS_SET = "governments"
SCHEMES_SET = "schemes"
TRANSACTIONS_SET = "transactions"
