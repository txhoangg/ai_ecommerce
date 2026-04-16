from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Attributes:
    data: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self.data

    def keys(self):
        return self.data.keys()

    def items(self):
        return self.data.items()

    def with_value(self, key: str, value: Any) -> 'Attributes':
        new_data = dict(self.data)
        new_data[key] = value
        return Attributes(new_data)

    def without_key(self, key: str) -> 'Attributes':
        new_data = {k: v for k, v in self.data.items() if k != key}
        return Attributes(new_data)

    def validate_against_schema(self, schema: Dict[str, Any]) -> list:
        errors = []
        for field_name, field_def in schema.items():
            if field_def.get('required', False) and field_name not in self.data:
                errors.append(f"Required attribute '{field_name}' is missing")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.data)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> 'Attributes':
        return cls(data or {})

    @classmethod
    def empty(cls) -> 'Attributes':
        return cls({})
