from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "comment-rate-service"})

from django.urls import path
from .views import (
    RatingCreate,
    RatingByBook,
    RatingByCustomer,
    ReviewCreate,
    ReviewByBook,
    ReviewByCustomer,
    ReviewDetail
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/ratings/', RatingCreate.as_view(), name='rating-create'),
    path('api/ratings/book/<int:book_id>/', RatingByBook.as_view(), name='rating-by-book'),
    path('api/ratings/customer/<int:customer_id>/', RatingByCustomer.as_view(), name='rating-by-customer'),
    path('api/reviews/', ReviewCreate.as_view(), name='review-create'),
    path('api/reviews/book/<int:book_id>/', ReviewByBook.as_view(), name='review-by-book'),
    path('api/reviews/customer/<int:customer_id>/', ReviewByCustomer.as_view(), name='review-by-customer'),
    path('api/reviews/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
]
