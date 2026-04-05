from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "ok", "service": "manager-service"})

from django.urls import path
from .views import (
    ManagerListCreate, ManagerDetail, ManagerLogin,
    ReportListCreate, ReportDetail,
    SalesReport, InventoryReport, CustomerReport, StaffReport,
    ManagerActivityList
)

urlpatterns = [
    path('health/', health, name='health'),
    # Manager endpoints (login before <int:pk> to avoid conflict)
    path('api/managers/', ManagerListCreate.as_view(), name='manager-list-create'),
    path('api/managers/login/', ManagerLogin.as_view(), name='manager-login'),
    path('api/managers/<int:pk>/', ManagerDetail.as_view(), name='manager-detail'),

    # Report generation endpoints (before generic <int:pk> to avoid conflict)
    path('api/reports/sales/', SalesReport.as_view(), name='sales-report'),
    path('api/reports/inventory/', InventoryReport.as_view(), name='inventory-report'),
    path('api/reports/customers/', CustomerReport.as_view(), name='customer-report'),
    path('api/reports/staff/', StaffReport.as_view(), name='staff-report'),
    path('api/reports/', ReportListCreate.as_view(), name='report-list-create'),
    path('api/reports/<int:pk>/', ReportDetail.as_view(), name='report-detail'),

    # Activity log
    path('api/activities/<int:manager_id>/', ManagerActivityList.as_view(), name='manager-activity-list'),
]
