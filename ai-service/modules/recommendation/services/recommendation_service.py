import requests
import logging
from typing import Optional
from django.conf import settings
from modules.graph.services.graph_service import graph_service
from modules.behavior.services.behavior_service import behavior_service
from modules.rag.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class RecommendationService:
    """Orchestrates personalized book recommendations using graph, behavior, and vector search."""

    def _fetch_book_details(self, book_id: int) -> Optional[dict]:
        """Fetch a single book's details from product-service."""
        try:
            resp = requests.get(
                f"{settings.PRODUCT_SERVICE_URL}/products/{book_id}/",
                timeout=5,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.warning(f"Could not fetch book {book_id}: {e}")
        return None

    def _fetch_books_list(self, params: dict = None) -> list:
        """Fetch a list of books from product-service with optional filter params."""
        try:
            request_params = dict(params or {})
            if 'limit' in request_params and 'page_size' not in request_params:
                request_params['page_size'] = request_params.pop('limit')
            resp = requests.get(
                f"{settings.PRODUCT_SERVICE_URL}/products/",
                params=request_params,
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get('results', data) if isinstance(data, dict) else data
        except Exception as e:
            logger.warning(f"Could not fetch books list: {e}")
        return []

    def get_personalized(self, user_id: int, limit: int = 10) -> list:
        """
        Get personalized book recommendations for a user.

        Strategy:
        1. Graph collaborative filtering (similar users' books)
        2. LSTM behavior: preferred book types
        3. Trending books as final fallback
        """
        # 1. Graph-based candidates
        graph_book_ids = graph_service.get_recommendations(user_id, limit=limit * 2)

        # 2. User behavior profile for preferred types
        profile = behavior_service.analyze_user(user_id)
        preferred_types = [p['type'] for p in profile.get('preferred_types', [])]

        # 3. Fetch details for graph candidates
        books = []
        seen_ids = set()

        for book_id in graph_book_ids:
            if len(books) >= limit:
                break
            book = self._fetch_book_details(book_id)
            if book and book['id'] not in seen_ids:
                seen_ids.add(book['id'])
                books.append(book)

        # 4. Fill with preferred-type books
        if len(books) < limit and preferred_types:
            for ptype in preferred_types:
                if len(books) >= limit:
                    break
                type_books = self._fetch_books_list({'book_type': ptype, 'limit': 5})
                for b in type_books:
                    if len(books) >= limit:
                        break
                    if b['id'] not in seen_ids:
                        seen_ids.add(b['id'])
                        books.append(b)

        # 5. Fill with trending books
        if len(books) < limit:
            trending_ids = graph_service.get_trending_books(limit=limit)
            for tid in trending_ids:
                if len(books) >= limit:
                    break
                if tid not in seen_ids:
                    book = self._fetch_book_details(tid)
                    if book:
                        seen_ids.add(tid)
                        books.append(book)

        # 6. Ultimate fallback: newest books
        if len(books) < limit:
            newest = self._fetch_books_list({'ordering': '-created_at', 'limit': limit})
            for b in newest:
                if len(books) >= limit:
                    break
                if b['id'] not in seen_ids:
                    seen_ids.add(b['id'])
                    books.append(b)

        return books[:limit]

    def get_similar_books(self, book_id: int, limit: int = 6) -> list:
        """
        Get books similar to the given book.

        Uses both graph co-interactions and vector similarity.
        """
        # Graph: co-viewed/co-purchased books
        similar_ids = graph_service.get_similar_books(book_id, limit=limit * 2)

        # Vector: semantically similar books
        vector_ids = []
        if book_id in vector_store.metadata:
            meta = vector_store.metadata[book_id]
            query = f"{meta.get('title', '')} {meta.get('book_type', '')} {meta.get('category', '')}"
            vector_results = vector_store.search(query, k=limit * 2)
            vector_ids = [v['book_id'] for v in vector_results if v['book_id'] != book_id]

        # Merge: graph candidates first, then vector
        all_ids = list(dict.fromkeys(similar_ids + vector_ids))

        books = []
        seen = set([book_id])  # exclude the source book

        for bid in all_ids:
            if len(books) >= limit:
                break
            if bid not in seen:
                book = self._fetch_book_details(bid)
                if book:
                    seen.add(bid)
                    books.append(book)

        return books

    def get_after_action(self, user_id: int, book_id: int, action: str, limit: int = 4) -> list:
        """
        Post-action recommendations triggered after a user action.
        Logs the interaction to the graph and returns similar books.
        """
        # Log interaction to graph
        graph_service.log_interaction(user_id, book_id, action)
        # Return similar books as next recommendations
        return self.get_similar_books(book_id, limit=limit)

    def get_new_arrivals(self, limit: int = 10) -> list:
        """Get newest books from product-service."""
        return self._fetch_books_list({'ordering': '-created_at', 'limit': limit})

    def get_by_type(self, book_type: str, limit: int = 10) -> list:
        """Get books filtered by type."""
        return self._fetch_books_list({'book_type': book_type, 'limit': limit})


recommendation_service = RecommendationService()
