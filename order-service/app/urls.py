from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "order-service"})

from django.urls import path
from .views import (
    OrderCreate,
    OrderDetail,
    OrderList,
    DiscountListCreate,
    DiscountValidate
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/orders/', OrderList.as_view(), name='order-list'),
    path('api/orders/create/', OrderCreate.as_view(), name='order-create'),
    path('api/orders/<int:pk>/', OrderDetail.as_view(), name='order-detail'),
    path('api/discounts/', DiscountListCreate.as_view(), name='discount-list-create'),
    path('api/discounts/validate/', DiscountValidate.as_view(), name='discount-validate'),
]
