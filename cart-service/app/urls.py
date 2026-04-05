from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "cart-service"})

from django.urls import path
from .views import (
    CartCreate,
    CartDetail,
    CartItemAdd,
    CartItemUpdate,
    CartList
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/carts/', CartCreate.as_view(), name='cart-create'),
    path('api/carts/all/', CartList.as_view(), name='cart-list'),
    path('api/carts/<int:customer_id>/', CartDetail.as_view(), name='cart-detail'),
    path('api/cart-items/', CartItemAdd.as_view(), name='cart-item-add'),
    path('api/cart-items/<int:pk>/', CartItemUpdate.as_view(), name='cart-item-update'),
]
