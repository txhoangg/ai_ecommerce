from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "customer-service"})

from django.urls import path
from .views import (
    CustomerListCreate,
    CustomerDetail,
    CustomerLogin,
    AddressListCreate
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/customers/', CustomerListCreate.as_view(), name='customer-list-create'),
    path('api/customers/login/', CustomerLogin.as_view(), name='customer-login'),
    path('api/customers/<int:pk>/', CustomerDetail.as_view(), name='customer-detail'),
    path('api/customers/<int:customer_id>/addresses/', AddressListCreate.as_view(), name='address-list-create'),
]
