from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "ship-service"})

from django.urls import path
from .views import (
    ShippingCreate,
    ShippingDetail,
    ShippingByOrder,
    ShippingTrack,
    ShippingList,
    CarrierListCreate
)

urlpatterns = [
    path('health/', health, name='health'),
    path('api/shipments/', ShippingCreate.as_view(), name='shipping-create'),
    path('api/shipments/all/', ShippingList.as_view(), name='shipping-list'),
    path('api/shipments/<int:pk>/', ShippingDetail.as_view(), name='shipping-detail'),
    path('api/shipments/order/<int:order_id>/', ShippingByOrder.as_view(), name='shipping-by-order'),
    path('api/shipments/track/<str:tracking_number>/', ShippingTrack.as_view(), name='shipping-track'),
    path('api/carriers/', CarrierListCreate.as_view(), name='carrier-list-create'),
]
