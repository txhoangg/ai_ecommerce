from django.urls import path
from .views import (
    PersonalizedRecommendView,
    SimilarBooksRecommendView,
    TrendingRecommendView,
    AfterActionView,
    NewArrivalsView,
    ByTypeView,
)

urlpatterns = [
    path('trending/', TrendingRecommendView.as_view(), name='recommend-trending'),
    path('after-action/', AfterActionView.as_view(), name='recommend-after-action'),
    path('new-arrivals/', NewArrivalsView.as_view(), name='recommend-new-arrivals'),
    path('by-type/<str:book_type>/', ByTypeView.as_view(), name='recommend-by-type'),
    path('similar/<int:book_id>/', SimilarBooksRecommendView.as_view(), name='recommend-similar'),
    path('<int:user_id>/', PersonalizedRecommendView.as_view(), name='recommend-personalized'),
]
