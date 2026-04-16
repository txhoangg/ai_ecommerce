from dataclasses import dataclass
from typing import Optional


@dataclass
class Publisher:
    name: str
    id: Optional[int] = None
    email: str = ''
    phone: str = ''
    address: str = ''
    website: str = ''

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
        }
