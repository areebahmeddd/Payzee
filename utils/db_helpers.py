import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(DateTimeEncoder, self).default(obj)


def serialize_for_db(data):
    """Serialize data to JSON string with datetime handling"""
    return json.dumps(data, cls=DateTimeEncoder)


def deserialize_from_db(json_str):
    """Deserialize JSON string back to Python object"""
    if json_str:
        return json.loads(json_str)
    return None
