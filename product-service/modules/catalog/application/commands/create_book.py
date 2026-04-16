from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class CreateBookCommand:
    title: str
    book_type_key: str
    description: str
    price: Decimal
    stock: int
    author: str = ''
    isbn: str = ''
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None
    image_url: str = ''
    attributes: dict = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))
        if self.price < Decimal('0'):
            raise ValueError("Price cannot be negative")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.book_type_key.strip():
            raise ValueError("Book type key cannot be empty")
