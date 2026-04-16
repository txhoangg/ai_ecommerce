import logging
from decimal import Decimal

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from modules.catalog.application.services.book_service import BookService
from modules.catalog.application.commands.create_book import CreateBookCommand
from modules.catalog.application.commands.update_book import UpdateBookCommand
from modules.catalog.application.queries.list_books import ListBooksQuery
from modules.catalog.infrastructure.models import BookTypeModel
from modules.catalog.presentation.api.serializers.book_serializers import (
    BookListSerializer, BookDetailSerializer,
    BookCreateSerializer, BookUpdateSerializer,
    BookTypeSerializer, BookStockUpdateSerializer
)
from shared.exceptions import (
    BookNotFoundException, BookTypeNotFoundException,
    InvalidBookDataException, InsufficientStockException
)

logger = logging.getLogger(__name__)


class BookListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        query = ListBooksQuery(
            book_type=request.query_params.get('book_type'),
            category_id=request.query_params.get('category_id'),
            publisher_id=request.query_params.get('publisher_id'),
            min_price=request.query_params.get('min_price'),
            max_price=request.query_params.get('max_price'),
            search=request.query_params.get('search'),
            is_active=request.query_params.get('is_active', 'true').lower() != 'false',
            ordering=request.query_params.get('ordering', '-created_at'),
        )

        service = BookService()
        books = service.list_books(query.to_filters())

        total = books.count()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        offset = (page - 1) * page_size
        paginated = books[offset:offset + page_size]

        serializer = BookListSerializer(paginated, many=True)
        return Response({
            'results': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        })

    def post(self, request):
        serializer = BookCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            command = CreateBookCommand(
                title=data['title'],
                author=data.get('author', ''),
                book_type_key=data['book_type_key'],
                description=data.get('description', ''),
                price=data['price'],
                stock=data.get('stock', 0),
                isbn=data.get('isbn', ''),
                publisher_id=data.get('publisher_id'),
                category_id=data.get('category_id'),
                image_url=data.get('image_url', ''),
                attributes=data.get('attributes', {}),
            )
            service = BookService()
            book = service.create_book(command)
            return Response(
                BookDetailSerializer(book).data,
                status=status.HTTP_201_CREATED
            )
        except BookTypeNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except InvalidBookDataException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating book: {e}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BookDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, book_id):
        service = BookService()
        try:
            book = service.get_book(book_id, active_only=True)
            return Response(BookDetailSerializer(book).data)
        except BookNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, book_id):
        return self._update(request, book_id, partial=False)

    def patch(self, request, book_id):
        return self._update(request, book_id, partial=True)

    def _update(self, request, book_id, partial=True):
        serializer = BookUpdateSerializer(data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            command = UpdateBookCommand(
                title=data.get('title'),
                author=data.get('author'),
                book_type_key=data.get('book_type_key'),
                description=data.get('description'),
                price=data.get('price'),
                stock=data.get('stock'),
                isbn=data.get('isbn'),
                publisher_id=data.get('publisher_id'),
                category_id=data.get('category_id'),
                image_url=data.get('image_url'),
                attributes=data.get('attributes'),
                is_active=data.get('is_active'),
            )
            service = BookService()
            book = service.update_book(book_id, command)
            return Response(BookDetailSerializer(book).data)
        except BookNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except (BookTypeNotFoundException, InvalidBookDataException) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error updating book {book_id}: {e}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, book_id):
        service = BookService()
        try:
            service.delete_book(book_id)
            return Response(
                {'message': f'Book {book_id} has been deactivated'},
                status=status.HTTP_200_OK
            )
        except BookNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class BookSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        service = BookService()
        books = service.search_books(query)

        total = books.count()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        offset = (page - 1) * page_size
        paginated = books[offset:offset + page_size]

        serializer = BookListSerializer(paginated, many=True)
        return Response({
            'query': query,
            'results': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
        })


class BookTypeListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        book_types = BookTypeModel.objects.all().order_by('type_key')
        serializer = BookTypeSerializer(book_types, many=True)
        return Response(serializer.data)


class BookStockUpdateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def patch(self, request, book_id):
        serializer = BookStockUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        service = BookService()

        try:
            if 'stock' in data:
                book = service.get_book(book_id, active_only=False)
                current_stock = book.stock
                delta = data['stock'] - current_stock
                book = service.update_stock(book_id, delta)
            else:
                book = service.update_stock(book_id, data['quantity_delta'])

            return Response({
                'id': book.id,
                'title': book.title,
                'stock': book.stock,
                'message': 'Stock updated successfully',
            })
        except BookNotFoundException as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except InsufficientStockException as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
