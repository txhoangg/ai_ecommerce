import requests
import logging
from django.conf import settings
from .deep_learning.user_embedder import user_embedder
from modules.graph.services.graph_service import graph_service

logger = logging.getLogger(__name__)


class BehaviorService:
    """Combines graph history and LSTM model to analyze user behavior."""

    def analyze_user(self, user_id: int) -> dict:
        """
        Build a behavioral profile for a user.

        Returns a dict with:
            segment: 'new' | 'browser' | 'buyer' | 'loyal'
            preferred_types: list of {type, probability}
            interaction_count: int
            purchase_count: int
        """
        history = graph_service.get_user_interaction_history(user_id)

        if not history:
            return {
                'segment': 'new',
                'preferred_types': [],
                'interaction_count': 0,
                'purchase_count': 0,
            }

        total_weight = sum(h.get('weight', 0) for h in history)
        purchase_count = sum(1 for h in history if h.get('last_event') == 'purchase')

        # Determine user segment
        if purchase_count >= 5:
            segment = 'loyal'
        elif purchase_count >= 1:
            segment = 'buyer'
        elif total_weight > 0:
            segment = 'browser'
        else:
            segment = 'new'

        # Get preferred book types from LSTM
        preferred_types_raw = user_embedder.get_preferred_types(history)
        preferred_types = [
            {'type': t, 'probability': round(p, 3)}
            for t, p in preferred_types_raw
        ]

        return {
            'segment': segment,
            'preferred_types': preferred_types,
            'interaction_count': len(history),
            'purchase_count': purchase_count,
            'total_weight': total_weight,
        }

    def get_trending_books_with_details(self, limit: int = 10) -> list:
        """Get trending book IDs then fetch full details from product-service."""
        trending_ids = graph_service.get_trending_books(limit=limit)

        if not trending_ids:
            # Fallback: fetch latest products from product-service
            try:
                params = {'ordering': '-created_at', 'page_size': limit}
                resp = requests.get(
                    f"{settings.PRODUCT_SERVICE_URL}/products/",
                    params=params,
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get('results', data) if isinstance(data, dict) else data
                    return items[:limit]
            except Exception as e:
                logger.warning(f"Could not fetch fallback trending books: {e}")
            return []

        # Fetch book details for each trending ID
        books = []
        for book_id in trending_ids:
            try:
                resp = requests.get(
                    f"{settings.PRODUCT_SERVICE_URL}/products/{book_id}/",
                    timeout=5,
                )
                if resp.status_code == 200:
                    books.append(resp.json())
            except Exception as e:
                logger.warning(f"Could not fetch book {book_id}: {e}")

        return books

    def log_and_analyze(self, user_id: int, book_id: int, event_type: str) -> dict:
        """Log an interaction and return updated user analysis."""
        graph_service.log_interaction(user_id, book_id, event_type)
        return self.analyze_user(user_id)


behavior_service = BehaviorService()
