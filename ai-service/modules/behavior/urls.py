from django.urls import path
from .views import (
    UserAnalysisView,
    TrendingBooksDetailView,
    LogAndAnalyzeView,
)

urlpatterns = [
    path('analyze/<int:user_id>/', UserAnalysisView.as_view(), name='behavior-analyze'),
    path('trending/', TrendingBooksDetailView.as_view(), name='behavior-trending'),
    path('log/', LogAndAnalyzeView.as_view(), name='behavior-log'),
]
