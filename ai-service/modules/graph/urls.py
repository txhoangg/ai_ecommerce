from django.urls import path
from .views import (
    LogInteractionView,
    TrendingBooksView,
    SimilarBooksView,
    AddBookView,
    UserRecommendationsView,
)

urlpatterns = [
    path('interaction/', LogInteractionView.as_view(), name='graph-log-interaction'),
    path('trending/', TrendingBooksView.as_view(), name='graph-trending'),
    path('similar/<int:book_id>/', SimilarBooksView.as_view(), name='graph-similar'),
    path('book/', AddBookView.as_view(), name='graph-add-book'),
    path('recommendations/<int:user_id>/', UserRecommendationsView.as_view(), name='graph-recommendations'),
]
