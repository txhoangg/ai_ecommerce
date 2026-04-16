from django.urls import path
from .views import (
    ChatView,
    SyncProductsView,
    AddProductView,
    SearchView,
    VectorStoreStatsView,
)

urlpatterns = [
    path('chat/', ChatView.as_view(), name='rag-chat'),
    path('sync/', SyncProductsView.as_view(), name='rag-sync'),
    path('product/', AddProductView.as_view(), name='rag-add-product'),
    path('search/', SearchView.as_view(), name='rag-search'),
    path('stats/', VectorStoreStatsView.as_view(), name='rag-stats'),
]
