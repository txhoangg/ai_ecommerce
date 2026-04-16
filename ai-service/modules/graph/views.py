from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.graph_service import graph_service
import logging

logger = logging.getLogger(__name__)


class LogInteractionView(APIView):
    """POST /api/graph/interaction/ - log user-book interaction"""

    def post(self, request):
        user_id = request.data.get('user_id') or request.data.get('customer_id')
        book_id = request.data.get('book_id')
        event_type = request.data.get('event_type', 'view')

        if not user_id or not book_id:
            return Response({'error': 'user_id and book_id required'}, status=400)

        valid_events = {'view', 'add_to_cart', 'purchase', 'search', 'rate'}
        if event_type not in valid_events:
            return Response({'error': f'event_type must be one of {valid_events}'}, status=400)

        graph_service.log_interaction(int(user_id), int(book_id), event_type)
        return Response({'status': 'logged', 'user_id': user_id, 'book_id': book_id, 'event_type': event_type})


class TrendingBooksView(APIView):
    """GET /api/graph/trending/ - get trending book IDs"""

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 100)
        book_ids = graph_service.get_trending_books(limit=limit)
        return Response({'book_ids': book_ids, 'count': len(book_ids)})


class SimilarBooksView(APIView):
    """GET /api/graph/similar/{book_id}/ - get similar book IDs"""

    def get(self, request, book_id):
        limit = int(request.query_params.get('limit', 6))
        limit = min(limit, 50)
        book_ids = graph_service.get_similar_books(int(book_id), limit=limit)
        return Response({'book_ids': book_ids, 'book_id': book_id})


class AddBookView(APIView):
    """POST /api/graph/book/ - register a book in the graph"""

    def post(self, request):
        book_id = request.data.get('book_id')
        book_type = request.data.get('book_type', 'fiction')
        category = request.data.get('category', '')

        if not book_id:
            return Response({'error': 'book_id required'}, status=400)

        graph_service.add_book_to_graph(int(book_id), book_type, category)
        return Response({'status': 'added', 'book_id': book_id})


class UserRecommendationsView(APIView):
    """GET /api/graph/recommendations/{user_id}/ - get graph-based recommendations"""

    def get(self, request, user_id):
        limit = int(request.query_params.get('limit', 10))
        book_ids = graph_service.get_recommendations(int(user_id), limit=limit)
        return Response({'book_ids': book_ids, 'user_id': user_id})
