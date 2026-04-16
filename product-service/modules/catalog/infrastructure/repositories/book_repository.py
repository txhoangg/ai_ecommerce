from typing import Optional, List
from django.db.models import QuerySet, Q
from modules.catalog.infrastructure.models import BookModel
from shared.exceptions import InsufficientStockException


class BookRepository:

    def get_by_id(self, book_id: int) -> Optional[BookModel]:
        try:
            return BookModel.objects.select_related(
                'book_type', 'category', 'publisher'
            ).get(id=book_id)
        except BookModel.DoesNotExist:
            return None

    def get_active_by_id(self, book_id: int) -> Optional[BookModel]:
        try:
            return BookModel.objects.select_related(
                'book_type', 'category', 'publisher'
            ).get(id=book_id, is_active=True)
        except BookModel.DoesNotExist:
            return None

    def list_all(self, filters: dict = None) -> QuerySet:
        qs = BookModel.objects.select_related(
            'book_type', 'category', 'publisher'
        )
        if filters:
            qs = self._apply_filters(qs, filters)
        return qs

    def _apply_filters(self, qs: QuerySet, filters: dict) -> QuerySet:
        if 'book_type' in filters and filters['book_type']:
            qs = qs.filter(book_type__type_key=filters['book_type'])

        if 'category_id' in filters and filters['category_id']:
            qs = qs.filter(category_id=filters['category_id'])

        if 'publisher_id' in filters and filters['publisher_id']:
            qs = qs.filter(publisher_id=filters['publisher_id'])

        if 'min_price' in filters and filters['min_price'] is not None:
            qs = qs.filter(price__gte=filters['min_price'])

        if 'max_price' in filters and filters['max_price'] is not None:
            qs = qs.filter(price__lte=filters['max_price'])

        if 'is_active' in filters and filters['is_active'] is not None:
            qs = qs.filter(is_active=filters['is_active'])

        if 'search' in filters and filters['search']:
            q = filters['search']
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(author__icontains=q) |
                Q(description__icontains=q) |
                Q(isbn__icontains=q)
            )

        ordering = filters.get('ordering', '-created_at')
        if ordering:
            qs = qs.order_by(ordering)

        return qs

    def search(self, query: str) -> QuerySet:
        return BookModel.objects.select_related(
            'book_type', 'category', 'publisher'
        ).filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query) |
            Q(isbn__icontains=query),
            is_active=True
        )

    def save(self, book: BookModel) -> BookModel:
        book.save()
        return book

    def delete(self, book_id: int) -> bool:
        try:
            book = BookModel.objects.get(id=book_id)
            book.is_active = False
            book.save()
            return True
        except BookModel.DoesNotExist:
            return False

    def update_stock(self, book_id: int, quantity_delta: int) -> Optional[BookModel]:
        try:
            book = BookModel.objects.get(id=book_id)
            new_stock = book.stock + quantity_delta
            if new_stock < 0:
                raise InsufficientStockException(
                    book_id=book.id,
                    requested=abs(quantity_delta),
                    available=book.stock,
                )
            book.stock = new_stock
            book.save()
            return book
        except BookModel.DoesNotExist:
            return None
