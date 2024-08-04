import json
from typing import TypeVar, get_args

T = TypeVar("T")

def __convert_to_serializable(obj: object) -> object:
    if isinstance(obj, list):
        arr = []
        for v in obj:
            arr.append(__convert_to_serializable(v))
        return arr
    elif not hasattr(obj, "__dict__"):
        return obj
    else:
        return obj.__dict__

def json_serialize(obj: object) -> str:
    return json.dumps(__convert_to_serializable(obj))

def json_deserialize(data: str, obj: T) -> T:
    if obj.__name__ != "list":
        target = obj.__new__(obj)
        for k, v in json.loads(data).items():
            target.__dict__[k] = v
        return target
    else:
        target = []
        entry_type = get_args(obj)[0]
        for v in json.loads(data):
            target.append(json_deserialize(json_serialize(v), entry_type))
        return target