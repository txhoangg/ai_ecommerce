from django.http import JsonResponse
from django.urls import path, include

from modules.rag.views import AddProductView


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'ai-service'})

urlpatterns = [
    path('health/', health, name='health'),
    path('api/graph/', include('modules.graph.urls')),
    path('api/rag/', include('modules.rag.urls')),
    path('api/behavior/', include('modules.behavior.urls')),
    path('api/recommend/', include('modules.recommendation.urls')),
    # Legacy compatibility route
    path('api/ai/', include('modules.rag.urls')),
    path('api/products/sync/', AddProductView.as_view(), name='product-sync-compat'),
]
