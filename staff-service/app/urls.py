from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "staff-service"})

from django.urls import path
from .views import (
    StaffListCreate,
    StaffDetail,
    StaffLogin,
    InventoryLogListCreate
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/staff/', StaffListCreate.as_view(), name='staff-list-create'),
    path('api/staff/login/', StaffLogin.as_view(), name='staff-login'),
    path('api/staff/<int:pk>/', StaffDetail.as_view(), name='staff-detail'),
    path('api/inventory-logs/', InventoryLogListCreate.as_view(), name='inventory-log-list-create'),
]
