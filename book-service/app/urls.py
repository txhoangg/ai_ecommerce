from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "book-service"})

from django.urls import path
from .views import (
    BookListCreate,
    BookDetail,
    BookStockUpdate,
    BookCheckStock
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/books/', BookListCreate.as_view(), name='book-list-create'),
    path('api/books/check-stock/', BookCheckStock.as_view(), name='book-check-stock'),
    path('api/books/<int:pk>/', BookDetail.as_view(), name='book-detail'),
    path('api/books/<int:pk>/stock/', BookStockUpdate.as_view(), name='book-stock-update'),
]
