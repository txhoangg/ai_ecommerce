from django.urls import path
from modules.catalog.presentation.api.views.book_views import (
    BookListCreateView, BookDetailView,
    BookSearchView, BookTypeListView, BookStockUpdateView
)
from modules.catalog.presentation.api.views.category_views import (
    CategoryListCreateView, CategoryDetailView
)
from modules.catalog.presentation.api.views.publisher_views import (
    PublisherListCreateView, PublisherDetailView
)

urlpatterns = [
    # Book / Product endpoints
    path('products/', BookListCreateView.as_view(), name='product-list-create'),
    path('products/search/', BookSearchView.as_view(), name='product-search'),
    path('products/types/', BookTypeListView.as_view(), name='product-types'),
    path('products/<int:book_id>/', BookDetailView.as_view(), name='product-detail'),
    path('products/<int:book_id>/stock/', BookStockUpdateView.as_view(), name='product-stock'),

    # Backward compatibility aliases
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/search/', BookSearchView.as_view(), name='book-search'),
    path('books/types/', BookTypeListView.as_view(), name='book-types'),
    path('books/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:book_id>/stock/', BookStockUpdateView.as_view(), name='book-stock'),

    # Category endpoints
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:category_id>/', CategoryDetailView.as_view(), name='category-detail'),

    # Publisher endpoints
    path('publishers/', PublisherListCreateView.as_view(), name='publisher-list-create'),
    path('publishers/<int:publisher_id>/', PublisherDetailView.as_view(), name='publisher-detail'),
]
