import json
from typing import TypeVar, get_args, get_type_hints

T = TypeVar("T")

def __convert_to_serializable(obj: object) -> object:
    if isinstance(obj, list):
        arr = []

        for entry in obj:
            arr.append(__convert_to_serializable(entry))

        return arr
    elif not hasattr(obj, "__dict__"):
        return obj
    else:
        fields = {}

        for field, value in obj.__dict__.items():
            fields[field] = __convert_to_serializable(value)
            
        return fields

def json_serialize(obj: object) -> str:
    return json.dumps(__convert_to_serializable(obj))

def json_deserialize(data: str | bytes | bytearray, obj: T) -> T:
    if obj.__name__ != "list":
        loaded = json.loads(data)
        if loaded.__class__.__name__ != "dict":
            if obj.__name__ == "dict":
                raise ValueError("Data was not a dictionary")
            return loaded
        elif obj.__name__ == "dict":
            return loaded
        
        target = obj.__new__(obj)
        target_type_hints = get_type_hints(target)

        for field, field_type in target_type_hints.items():
            if field_type.__name__ == "Optional":
                target.__dict__[field] = None

        for field, value in loaded.items():
            if not field in target_type_hints:
                print(f"{target.__class__.__name__} has no type hint for {field}")
                target.__dict__[field] = value
                continue

            field_type = target_type_hints[field]
            target.__dict__[field] = json_deserialize(json_serialize(value), field_type)

        return target
    else:
        target = []
        entry_type = get_args(obj)[0]

        for entry in json.loads(data):
            target.append(json_deserialize(json_serialize(entry), entry_type))

        return target