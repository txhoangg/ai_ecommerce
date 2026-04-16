from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass
class ListBooksQuery:
    book_type: Optional[str] = None
    category_id: Optional[int] = None
    publisher_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    search: Optional[str] = None
    is_active: Optional[bool] = True
    ordering: str = '-created_at'
    page: int = 1
    page_size: int = 20

    def to_filters(self) -> dict:
        filters = {}
        if self.book_type:
            filters['book_type'] = self.book_type
        if self.category_id is not None:
            filters['category_id'] = self.category_id
        if self.publisher_id is not None:
            filters['publisher_id'] = self.publisher_id
        if self.min_price is not None:
            filters['min_price'] = self.min_price
        if self.max_price is not None:
            filters['max_price'] = self.max_price
        if self.search:
            filters['search'] = self.search
        if self.is_active is not None:
            filters['is_active'] = self.is_active
        filters['ordering'] = self.ordering
        return filters
