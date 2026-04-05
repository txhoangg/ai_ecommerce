from django.http import JsonResponse
from django.urls import path
from .views import RecommendationList, GenerateRecommendations, PopularBooks
from .ai_views import (
    KBBuildView, KBQueryView, KBStatsView,
    ChatView, ChatHistoryView,
    BehaviorModelTrainView, BehaviorModelRecommendView,
    AIStatusView,
)

def health(request):
    return JsonResponse({"status": "ok", "service": "recommender-ai-service"})

urlpatterns = [
    path('health/', health, name='health'),
    # Existing recommendation endpoints
    path('api/recommendations/generate/', GenerateRecommendations.as_view(), name='generate-recommendations'),
    path('api/recommendations/popular/', PopularBooks.as_view(), name='popular-books'),
    path('api/recommendations/<int:customer_id>/', RecommendationList.as_view(), name='recommendation-list'),
    # AI: Knowledge Base
    path('api/ai/kb/build/', KBBuildView.as_view(), name='kb-build'),
    path('api/ai/kb/query/', KBQueryView.as_view(), name='kb-query'),
    path('api/ai/kb/stats/', KBStatsView.as_view(), name='kb-stats'),
    # AI: RAG Chat
    path('api/ai/chat/', ChatView.as_view(), name='chat'),
    path('api/ai/chat/<str:session_id>/history/', ChatHistoryView.as_view(), name='chat-history'),
    # AI: Behavior Model (NCF)
    path('api/ai/model/train/', BehaviorModelTrainView.as_view(), name='model-train'),
    path('api/ai/model/recommend/<int:customer_id>/', BehaviorModelRecommendView.as_view(), name='model-recommend'),
    # AI: Status
    path('api/ai/status/', AIStatusView.as_view(), name='ai-status'),
]
