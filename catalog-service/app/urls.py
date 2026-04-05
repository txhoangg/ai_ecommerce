from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "catalog-service"})

from django.urls import path
from .views import (
    CategoryListCreate,
    CategoryDetail,
    PublisherListCreate,
    PublisherDetail,
    BookSeriesListCreate,
    BookSeriesDetail
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('api/categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('api/publishers/', PublisherListCreate.as_view(), name='publisher-list-create'),
    path('api/publishers/<int:pk>/', PublisherDetail.as_view(), name='publisher-detail'),
    path('api/book-series/', BookSeriesListCreate.as_view(), name='book-series-list-create'),
    path('api/book-series/<int:pk>/', BookSeriesDetail.as_view(), name='book-series-detail'),
]
