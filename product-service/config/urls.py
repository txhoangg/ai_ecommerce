from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health(request):
    return JsonResponse({'status': 'ok', 'service': 'product-service'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    path('', include('modules.catalog.presentation.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
