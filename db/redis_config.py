import redis

# Initialize Redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

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
