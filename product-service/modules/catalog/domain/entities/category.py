from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    name: str
    slug: str
    id: Optional[int] = None
    description: str = ''
    parent_id: Optional[int] = None

    def is_root(self) -> bool:
        return self.parent_id is None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': self.parent_id,
        }
