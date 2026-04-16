from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class UpdateBookCommand:
    title: Optional[str] = None
    book_type_key: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    isbn: Optional[str] = None
    publisher_id: Optional[int] = None
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    attributes: Optional[dict] = None
    is_active: Optional[bool] = None

    def __post_init__(self):
        if self.price is not None:
            if not isinstance(self.price, Decimal):
                self.price = Decimal(str(self.price))
            if self.price < Decimal('0'):
                raise ValueError("Price cannot be negative")
        if self.stock is not None and self.stock < 0:
            raise ValueError("Stock cannot be negative")

    def get_updates(self) -> dict:
        updates = {}
        if self.title is not None:
            updates['title'] = self.title
        if self.author is not None:
            updates['author'] = self.author
        if self.description is not None:
            updates['description'] = self.description
        if self.price is not None:
            updates['price'] = self.price
        if self.stock is not None:
            updates['stock'] = self.stock
        if self.isbn is not None:
            updates['isbn'] = self.isbn
        if self.publisher_id is not None:
            updates['publisher_id'] = self.publisher_id
        if self.category_id is not None:
            updates['category_id'] = self.category_id
        if self.image_url is not None:
            updates['image_url'] = self.image_url
        if self.attributes is not None:
            updates['attributes'] = self.attributes
        if self.is_active is not None:
            updates['is_active'] = self.is_active
        return updates
