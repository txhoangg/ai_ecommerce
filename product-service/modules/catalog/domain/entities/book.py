from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class Book:
    title: str
    book_type: str
    description: str
    price: Decimal
    stock: int
    id: Optional[int] = None
    isbn: Optional[str] = None
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    attributes: dict = field(default_factory=dict)
    is_active: bool = True

    def is_in_stock(self) -> bool:
        return self.stock > 0

    def apply_discount(self, percent: float) -> Decimal:
        discount_amount = self.price * Decimal(str(percent / 100))
        return self.price - discount_amount

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'book_type': self.book_type,
            'description': self.description,
            'price': str(self.price),
            'stock': self.stock,
            'isbn': self.isbn,
            'publisher_id': self.publisher_id,
            'category_id': self.category_id,
            'image_url': self.image_url,
            'attributes': self.attributes,
            'is_active': self.is_active,
        }
