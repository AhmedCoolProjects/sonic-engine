from dataclasses import _MISSING_TYPE, dataclass, fields, is_dataclass
from sonic_engine.util.functions import EngineUtil

engine_util = EngineUtil()


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)

        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            missing = []
            for f in fields(cls):
                if type(f.default) == _MISSING_TYPE and f.name not in kwargs:
                    missing.append(f"{f.name}")
            if len(missing):
                parent_key = (
                    cls._parent_key + "."
                    if hasattr(cls, "_parent_key") and cls._parent_key
                    else ""
                )
                missing_fields = ",".join([f"'{parent_key}{f}'" for f in missing])
                raise TypeError(
                    f"The following fields {missing_fields} are required for {cls.__name__}"
                )

            for name, value in kwargs.items():
                field_type = None
                for f in fields(cls):
                    if f.name == name:
                        field_type = f.type
                        break
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj
            try:
                original_init(self, *args, **kwargs)
            except TypeError as e:
                engine_util.logger.error(f"{e} for {cls.__name__}")

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper
