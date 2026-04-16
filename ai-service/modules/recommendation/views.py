from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.recommendation_service import recommendation_service
from modules.graph.services.graph_service import graph_service
import logging

logger = logging.getLogger(__name__)


class PersonalizedRecommendView(APIView):
    """GET /api/recommend/{user_id}/ - personalized recommendations for a user"""

    def get(self, request, user_id):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)
        books = recommendation_service.get_personalized(int(user_id), limit=limit)
        return Response({'books': books, 'user_id': user_id, 'count': len(books)})


class SimilarBooksRecommendView(APIView):
    """GET /api/recommend/similar/{book_id}/ - books similar to a given book"""

    def get(self, request, book_id):
        limit = int(request.query_params.get('limit', 6))
        limit = min(limit, 30)
        books = recommendation_service.get_similar_books(int(book_id), limit=limit)
        return Response({'books': books, 'book_id': book_id, 'count': len(books)})


class TrendingRecommendView(APIView):
    """GET /api/recommend/trending/ - trending book IDs from graph"""

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 100)
        book_ids = graph_service.get_trending_books(limit=limit)
        return Response({'book_ids': book_ids, 'count': len(book_ids)})


class AfterActionView(APIView):
    """POST /api/recommend/after-action/ - recommendations after a user action"""

    def post(self, request):
        user_id = request.data.get('user_id') or request.data.get('customer_id')
        book_id = request.data.get('book_id')
        action = request.data.get('action', 'view')
        limit = int(request.data.get('limit', 4))

        if not user_id or not book_id:
            return Response({'error': 'user_id and book_id required'}, status=400)

        valid_actions = {'view', 'add_to_cart', 'purchase', 'rate'}
        if action not in valid_actions:
            return Response({'error': f'action must be one of {valid_actions}'}, status=400)

        books = recommendation_service.get_after_action(
            int(user_id), int(book_id), action, limit=limit
        )
        return Response({'books': books, 'action': action, 'book_id': book_id})


class NewArrivalsView(APIView):
    """GET /api/recommend/new-arrivals/ - newest books"""

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)
        books = recommendation_service.get_new_arrivals(limit=limit)
        return Response({'books': books, 'count': len(books)})


class ByTypeView(APIView):
    """GET /api/recommend/by-type/{book_type}/ - books by type"""

    def get(self, request, book_type):
        limit = int(request.query_params.get('limit', 10))
        limit = min(limit, 50)
        books = recommendation_service.get_by_type(book_type, limit=limit)
        return Response({'books': books, 'book_type': book_type, 'count': len(books)})
