import logging
import threading
from typing import Optional
from decimal import Decimal

import requests
from django.conf import settings
from django.db.models import QuerySet

from modules.catalog.infrastructure.models import (
    BookModel, BookTypeModel, CategoryModel, PublisherModel
)
from modules.catalog.infrastructure.repositories.book_repository import BookRepository
from modules.catalog.application.commands.create_book import CreateBookCommand
from modules.catalog.application.commands.update_book import UpdateBookCommand
from shared.exceptions import (
    BookNotFoundException, BookTypeNotFoundException,
    InvalidBookDataException
)

logger = logging.getLogger(__name__)


class BookService:

    def __init__(self):
        self.repository = BookRepository()

    def create_book(self, command: CreateBookCommand) -> BookModel:
        try:
            book_type = BookTypeModel.objects.get(type_key=command.book_type_key)
        except BookTypeModel.DoesNotExist:
            raise BookTypeNotFoundException(
                f"Book type '{command.book_type_key}' not found"
            )

        category = None
        if command.category_id:
            try:
                category = CategoryModel.objects.get(id=command.category_id)
            except CategoryModel.DoesNotExist:
                raise InvalidBookDataException(
                    f"Category with id {command.category_id} not found"
                )

        publisher = None
        if command.publisher_id:
            try:
                publisher = PublisherModel.objects.get(id=command.publisher_id)
            except PublisherModel.DoesNotExist:
                raise InvalidBookDataException(
                    f"Publisher with id {command.publisher_id} not found"
                )

        book = BookModel(
            title=command.title,
            author=command.author,
            book_type=book_type,
            category=category,
            publisher=publisher,
            description=command.description,
            price=command.price,
            stock=command.stock,
            isbn=command.isbn,
            image_url=command.image_url,
            attributes=command.attributes,
            is_active=True,
        )
        book = self.repository.save(book)

        self._dispatch_ai_sync(book)

        return book

    def update_book(self, book_id: int, command: UpdateBookCommand) -> BookModel:
        book = self.repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(f"Book with id {book_id} not found")

        if command.book_type_key:
            try:
                book_type = BookTypeModel.objects.get(type_key=command.book_type_key)
                book.book_type = book_type
            except BookTypeModel.DoesNotExist:
                raise BookTypeNotFoundException(
                    f"Book type '{command.book_type_key}' not found"
                )

        updates = command.get_updates()
        for field_name, value in updates.items():
            if field_name == 'publisher_id' and value is not None:
                try:
                    book.publisher = PublisherModel.objects.get(id=value)
                except PublisherModel.DoesNotExist:
                    raise InvalidBookDataException(
                        f"Publisher with id {value} not found"
                    )
            elif field_name == 'category_id' and value is not None:
                try:
                    book.category = CategoryModel.objects.get(id=value)
                except CategoryModel.DoesNotExist:
                    raise InvalidBookDataException(
                        f"Category with id {value} not found"
                    )
            else:
                setattr(book, field_name, value)

        book = self.repository.save(book)
        self._dispatch_ai_sync(book)
        return book

    def get_book(self, book_id: int, active_only: bool = True) -> BookModel:
        if active_only:
            book = self.repository.get_active_by_id(book_id)
        else:
            book = self.repository.get_by_id(book_id)

        if not book:
            raise BookNotFoundException(f"Book with id {book_id} not found")
        return book

    def list_books(self, filters: dict = None) -> QuerySet:
        return self.repository.list_all(filters or {})

    def search_books(self, query: str) -> QuerySet:
        return self.repository.search(query)

    def update_stock(self, book_id: int, quantity_delta: int) -> BookModel:
        book = self.repository.update_stock(book_id, quantity_delta)
        if not book:
            raise BookNotFoundException(f"Book with id {book_id} not found")
        return book

    def delete_book(self, book_id: int) -> bool:
        book = self.repository.get_by_id(book_id)
        if not book:
            raise BookNotFoundException(f"Book with id {book_id} not found")
        deleted = self.repository.delete(book_id)
        if deleted:
            book.is_active = False
            self._dispatch_ai_sync(book)
        return deleted

    def create_book_from_data(self, data: dict) -> BookModel:
        """Create a book directly from a validated data dict (e.g. from serializer)."""
        book_type = data.pop('book_type_key', None)
        if book_type is None:
            raise InvalidBookDataException("book_type_key is required")
        # book_type may already be a BookTypeModel instance (resolved by serializer)
        if not isinstance(book_type, BookTypeModel):
            try:
                book_type = BookTypeModel.objects.get(type_key=book_type)
            except BookTypeModel.DoesNotExist:
                raise BookTypeNotFoundException(f"Book type '{book_type}' not found")

        book = BookModel(book_type=book_type, **data)
        book = self.repository.save(book)

        self._dispatch_ai_sync(book)
        return book

    def _dispatch_ai_sync(self, book: BookModel):
        thread = threading.Thread(
            target=self._sync_book_to_ai_services,
            args=(book,),
            daemon=True,
        )
        thread.start()

    def _sync_book_to_ai_services(self, book: BookModel):
        try:
            ai_service_url = getattr(settings, 'AI_SERVICE_URL', 'http://ai-service:8013')
            rag_payload = {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'description': book.description,
                'book_type_key': book.book_type.type_key,
                'category_name': book.category.name if book.category else '',
                'price': float(book.price),
                'attributes': book.attributes,
                'is_active': book.is_active,
            }
            graph_payload = {
                'book_id': book.id,
                'book_type': book.book_type.type_key,
                'category': book.category.name if book.category else '',
            }

            rag_response = requests.post(
                f"{ai_service_url}/api/rag/product/",
                json=rag_payload,
                timeout=5
            )
            graph_response = requests.post(
                f"{ai_service_url}/api/graph/book/",
                json=graph_payload,
                timeout=5,
            )

            if rag_response.status_code not in (200, 201):
                logger.warning(
                    f"RAG sync returned {rag_response.status_code} for book {book.id}"
                )
            if graph_response.status_code not in (200, 201):
                logger.warning(
                    f"Graph sync returned {graph_response.status_code} for book {book.id}"
                )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to sync AI services for book {book.id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error syncing AI services: {e}")
