import json
from datetime import datetime
from typing import Any, Dict, Optional


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


def serialize_for_db(data: Dict[str, Any]) -> str:
    """Serialize data to JSON string with datetime handling"""
    if data is None:
        return "{}"
    return json.dumps(data, cls=DateTimeEncoder)


def deserialize_from_db(json_str: Optional[bytes]) -> Optional[Dict[str, Any]]:
    """Deserialize JSON string back to Python object"""
    if json_str:
        return json.loads(json_str)
    return None
