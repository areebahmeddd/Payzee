import time
import functools
from typing import Any, Dict, List, Optional
from .redis_config import redis_client
from utils.db_helpers import serialize_for_db, deserialize_from_db
from monitoring.metrics import REDIS_QUERY_TIME


def track_db_operation(func):
    """Decorator to track Redis operation execution time"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        collection = args[0] if args else kwargs.get("collection_prefix", "unknown")
        operation = func.__name__

        # Start timing
        start_time = time.time()

        try:
            # Execute the function
            result = func(*args, **kwargs)
            return result
        finally:
            # Record the time taken
            duration = time.time() - start_time
            REDIS_QUERY_TIME.labels(operation=operation, collection=collection).observe(
                duration
            )

    return wrapper


@track_db_operation
def get_document(collection_prefix: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """Get a document from Redis by ID"""
    key = f"{collection_prefix}{doc_id}"
    data = redis_client.get(key)
    return deserialize_from_db(data)


@track_db_operation
def set_document(
    collection_prefix: str,
    doc_id: str,
    data: Dict[str, Any],
    index_set: Optional[str] = None,
) -> str:
    """Save a document to Redis"""
    key = f"{collection_prefix}{doc_id}"
    redis_client.set(key, serialize_for_db(data))
    # Add to index set if provided
    if index_set:
        redis_client.sadd(index_set, doc_id)
    return doc_id


@track_db_operation
def delete_document(
    collection_prefix: str, doc_id: str, index_set: Optional[str] = None
) -> bool:
    """Delete a document from Redis"""
    key = f"{collection_prefix}{doc_id}"
    redis_client.delete(key)
    # Remove from index set if provided
    if index_set:
        redis_client.srem(index_set, doc_id)
    return True


@track_db_operation
def get_all_documents(collection_prefix: str, index_set: str) -> List[Dict[str, Any]]:
    """Get all documents of a specific type"""
    result = []
    all_ids = redis_client.smembers(index_set)
    for doc_id in all_ids:
        data = get_document(collection_prefix, doc_id)
        if data:
            result.append(data)
    return result


@track_db_operation
def query_by_field(
    collection_prefix: str, index_set: str, field_path: str, value: Any
) -> List[Dict[str, Any]]:
    """Query documents where a field equals a value"""
    result = []
    all_ids = redis_client.smembers(index_set)

    # Handle nested fields with dot notation
    field_parts = field_path.split(".")

    for doc_id in all_ids:
        data = get_document(collection_prefix, doc_id)
        if data:
            # Navigate to the nested field
            current = data
            found = True
            for part in field_parts:
                if part in current:
                    current = current[part]
                else:
                    found = False
                    break

            if found and current == value:
                data["id"] = doc_id
                result.append(data)

    return result


@track_db_operation
def update_document(
    collection_prefix: str, doc_id: str, update_data: Dict[str, Any]
) -> bool:
    """Update a document in Redis"""
    data = get_document(collection_prefix, doc_id)
    if data:
        # Handle nested field updates
        for key, value in update_data.items():
            # Handle nested fields with dot notation
            parts = key.split(".")
            target = data

            # Navigate to the nested location
            for i, part in enumerate(parts):
                if i == len(parts) - 1:  # Last part is the field to update
                    target[part] = value
                else:  # Navigate deeper into the structure
                    if part not in target:
                        target[part] = {}
                    target = target[part]

        # Update the document
        set_document(collection_prefix, doc_id, data)
        return True
    return False


@track_db_operation
def array_union(
    collection_prefix: str, doc_id: str, field_path: str, values: List[Any]
) -> bool:
    """Adds values to an array field, avoiding duplicates"""
    data = get_document(collection_prefix, doc_id)
    if data:
        # Handle nested fields with dot notation
        parts = field_path.split(".")
        target = data

        # Navigate to the nested location
        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # Last part is the field to update
                if part not in target:
                    target[part] = []

                # Add values, ensuring no duplicates
                current_array = target[part]
                for value in values:
                    if value not in current_array:
                        current_array.append(value)

                target[part] = current_array
            else:  # Navigate deeper
                if part not in target:
                    target[part] = {}
                target = target[part]

        # Update the document
        set_document(collection_prefix, doc_id, data)
        return True
    return False
