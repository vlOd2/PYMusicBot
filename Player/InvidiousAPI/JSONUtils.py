import json
from typing import Any, TypeVar, get_args, get_type_hints

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
        fields = {}

        for k, v in obj.__dict__.items():
            fields[k] = __convert_to_serializable(v)
            
        return fields

def json_serialize(obj: object) -> str:
    return json.dumps(__convert_to_serializable(obj))

def json_deserialize(data: str | bytes | bytearray, obj: T) -> T:
    if obj.__name__ != "list":
        loaded = json.loads(data)
        if loaded.__class__.__name__ != "dict":
            return loaded
        
        if obj.__name__ == "dict":
            return loaded
        
        target = obj.__new__(obj)
        target_type_hints = get_type_hints(target)
        for k, v in loaded.items():
            if not k in target_type_hints:
                print(f"{target.__class__.__name__} has no type hint for {k}")
                target.__dict__[k] = v
                continue

            field_type = target_type_hints[k]
            target.__dict__[k] = json_deserialize(json_serialize(v), field_type)

        return target
    else:
        target = []
        entry_type = get_args(obj)[0]

        for v in json.loads(data):
            target.append(json_deserialize(json_serialize(v), entry_type))

        return target