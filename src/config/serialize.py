from uuid import UUID
from datetime import datetime


def _serialize_dict(data):
    return {str(serialize(key)): serialize(value)
            for key, value in data.items()}


def _serialize_list(data):
    return [serialize(x) for x in data]


def serialize(data):
    """Flatten any simple data structures to JSON-ifyable types."""
    if callable(data):
        # We're (hopefully) using serialize as a decorator
        def serialization_wrapper(*args, **kwargs):
            return serialize(data(*args, **kwargs))
        return serialization_wrapper
    if isinstance(data, dict):
        return _serialize_dict(data)
    elif isinstance(data, list):
        return _serialize_list(data)
    elif isinstance(data, tuple):
        return tuple(serialize(x) for x in data)
    elif isinstance(data, UUID):
        return str(data)
    elif isinstance(data, datetime):
        # Convert dates to epoch millis
        return int(data.timestamp() * 1000)
    else:
        return data
