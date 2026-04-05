from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "pay-service"})

from django.urls import path
from .views import (
    PaymentCreate,
    PaymentDetail,
    PaymentByOrder,
    PaymentList
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/payments/', PaymentCreate.as_view(), name='payment-create'),
    path('api/payments/all/', PaymentList.as_view(), name='payment-list'),
    path('api/payments/<int:pk>/', PaymentDetail.as_view(), name='payment-detail'),
    path('api/payments/order/<int:order_id>/', PaymentByOrder.as_view(), name='payment-by-order'),
]
