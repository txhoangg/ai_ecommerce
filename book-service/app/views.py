from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer, BookListSerializer, BookStockUpdateSerializer
import requests
from django.conf import settings


class BookListCreate(APIView):
    """
    GET: List all books (with optional filters)
    POST: Create new book (staff only)
    """
    
    def get(self, request):
        books = Book.objects.all()
        
        # Filter by category
        category_id = request.query_params.get('category_id')
        if category_id:
            books = books.filter(category_id=category_id)
        
        # Filter by search query
        search = request.query_params.get('search')
        if search:
            books = books.filter(title__icontains=search) | books.filter(author__icontains=search)
        
        # Use simplified serializer for list
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            book = serializer.save()
            
            # Log inventory action to staff-service
            if book.staff_id:
                try:
                    requests.post(
                        f"{settings.STAFF_SERVICE_URL}/api/inventory-logs/",
                        json={
                            'staff_id': book.staff_id,
                            'book_id': book.id,
                            'action': 'created',
                            'quantity': book.stock
                        },
                        timeout=5
                    )
                except requests.exceptions.RequestException:
                    pass  # Log failed but book created
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    """
    GET: Retrieve book details
    PUT: Update book (staff only)
    DELETE: Delete book (staff only)
    """
    
    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return None
    
    def get(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSerializer(book)
        return Response(serializer.data)
    
    def put(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        old_stock = book.stock
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            book = serializer.save()
            
            # Log stock change if stock was updated
            if 'stock' in request.data and book.stock != old_stock:
                staff_id = request.data.get('staff_id', book.staff_id)
                if staff_id:
                    try:
                        requests.post(
                            f"{settings.STAFF_SERVICE_URL}/api/inventory-logs/",
                            json={
                                'staff_id': staff_id,
                                'book_id': book.id,
                                'action': 'updated',
                                'quantity': book.stock - old_stock
                            },
                            timeout=5
                        )
                    except requests.exceptions.RequestException:
                        pass
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookStockUpdate(APIView):
    """
    POST: Update book stock
    """
    
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookStockUpdateSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            action = serializer.validated_data['action']
            
            old_stock = book.stock
            
            if action == 'add':
                book.stock += quantity
            elif action == 'subtract':
                if book.stock < quantity:
                    return Response({
                        'error': 'Insufficient stock',
                        'current_stock': book.stock,
                        'requested': quantity
                    }, status=status.HTTP_400_BAD_REQUEST)
                book.stock -= quantity
            elif action == 'set':
                book.stock = quantity
            
            book.save()
            
            return Response({
                'id': book.id,
                'title': book.title,
                'old_stock': old_stock,
                'new_stock': book.stock,
                'action': action
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookCheckStock(APIView):
    """
    POST: Check if books are in stock (bulk check)
    """
    
    def post(self, request):
        book_ids = request.data.get('book_ids', [])
        if not book_ids:
            return Response({'error': 'book_ids required'}, status=status.HTTP_400_BAD_REQUEST)
        
        books = Book.objects.filter(id__in=book_ids)
        result = []
        
        for book in books:
            result.append({
                'id': book.id,
                'title': book.title,
                'stock': book.stock,
                'in_stock': book.stock > 0
            })
        
        return Response(result)
