"""
Health and Metrics endpoints - Assignment 06 Observability
"""

import time
import threading
from django.http import JsonResponse
from django.conf import settings
import requests

_start_time = time.time()
_request_count = 0
_request_count_lock = threading.Lock()


def increment_request_count():
    global _request_count
    with _request_count_lock:
        _request_count += 1


def health(request):
    """
    GET /health/
    Returns health status of the API Gateway and all downstream services.
    """
    service_urls = {
        'staff-service': settings.STAFF_SERVICE_URL,
        'manager-service': settings.MANAGER_SERVICE_URL,
        'customer-service': settings.CUSTOMER_SERVICE_URL,
        'product-service': settings.PRODUCT_SERVICE_URL,
        'cart-service': settings.CART_SERVICE_URL,
        'order-service': settings.ORDER_SERVICE_URL,
        'ship-service': settings.SHIP_SERVICE_URL,
        'pay-service': settings.PAY_SERVICE_URL,
        'comment-rate-service': settings.COMMENT_RATE_SERVICE_URL,
        'ai-service': settings.AI_SERVICE_URL,
    }

    services_status = {}
    all_healthy = True

    for name, url in service_urls.items():
        try:
            resp = requests.get(f"{url}/health/", timeout=3)
            ok = resp.status_code == 200
        except Exception:
            ok = False
        services_status[name] = 'healthy' if ok else 'unreachable'
        if not ok:
            all_healthy = False

    return JsonResponse({
        'status': 'healthy' if all_healthy else 'degraded',
        'service': 'api-gateway',
        'uptime_seconds': int(time.time() - _start_time),
        'downstream_services': services_status,
    })


def metrics(request):
    """
    GET /metrics/
    Returns basic runtime metrics of the API Gateway.
    """
    return JsonResponse({
        'service': 'api-gateway',
        'uptime_seconds': int(time.time() - _start_time),
        'total_requests': _request_count,
        'python_version': __import__('sys').version,
        'django_version': __import__('django').get_version(),
    })
