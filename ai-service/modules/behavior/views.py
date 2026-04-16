from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.behavior_service import behavior_service
import logging

logger = logging.getLogger(__name__)


class UserAnalysisView(APIView):
    """GET /api/behavior/analyze/{user_id}/ - analyze user behavior profile"""

    def get(self, request, user_id):
        result = behavior_service.analyze_user(int(user_id))
        return Response(result)


class TrendingBooksDetailView(APIView):
    """GET /api/behavior/trending/ - trending books with full product details"""

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)
        books = behavior_service.get_trending_books_with_details(limit=limit)
        return Response({'books': books, 'count': len(books)})


class LogAndAnalyzeView(APIView):
    """POST /api/behavior/log/ - log interaction and return updated user profile"""

    def post(self, request):
        user_id = request.data.get('user_id') or request.data.get('customer_id')
        book_id = request.data.get('book_id')
        event_type = request.data.get('event_type', 'view')

        if not user_id or not book_id:
            return Response({'error': 'user_id and book_id required'}, status=400)

        result = behavior_service.log_and_analyze(int(user_id), int(book_id), event_type)
        return Response(result)
