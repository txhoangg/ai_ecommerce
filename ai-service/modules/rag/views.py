from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .services.rag_service import rag_service
from .services.vector_store import vector_store
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """POST /api/rag/chat/ - RAG-powered chat assistant"""
    permission_classes = [AllowAny]

    def post(self, request):
        messages = request.data.get('messages', [])
        user_id = request.data.get('user_id') or request.data.get('customer_id')

        # Support single-message format
        if not messages:
            message = request.data.get('message', '')
            if message:
                messages = [{'role': 'user', 'content': message}]
            else:
                return Response({'error': 'messages or message field required'}, status=400)

        result = rag_service.chat(messages, user_id=user_id)
        return Response(result)


class SyncProductsView(APIView):
    """POST /api/rag/sync/ - sync all products from product-service to FAISS"""

    def post(self, request):
        try:
            count = 0
            page = 1
            page_size = min(int(request.data.get('page_size', 200)), 500)

            while True:
                resp = requests.get(
                    f"{settings.PRODUCT_SERVICE_URL}/products/",
                    params={'page': page, 'page_size': page_size},
                    timeout=30,
                )
                if resp.status_code != 200:
                    return Response({'error': f'Failed to fetch products: HTTP {resp.status_code}'}, status=500)

                data = resp.json()
                products = data.get('results', data) if isinstance(data, dict) else data
                if not products:
                    break

                for product in products:
                    try:
                        vector_store.add_book(
                            book_id=int(product['id']),
                            title=product.get('title', ''),
                            author=product.get('author', ''),
                            description=product.get('description', ''),
                            book_type=product.get('book_type_key', 'fiction'),
                            category=product.get('category_name', ''),
                            price=float(product.get('price', 0)),
                            attributes=product.get('attributes', {}),
                            is_active=product.get('is_active', True),
                        )
                        count += 1
                    except Exception as e:
                        logger.warning(f"Failed to index product {product.get('id')}: {e}")

                total_pages = data.get('total_pages', 1) if isinstance(data, dict) else 1
                if page >= total_pages:
                    break
                page += 1

            return Response({'synced': count, 'total_in_index': vector_store.get_stats()['total_vectors']})
        except requests.exceptions.ConnectionError:
            logger.warning("Product service not reachable during sync")
            return Response({'error': 'Product service not reachable', 'synced': 0}, status=503)
        except Exception as e:
            logger.error(f"Sync error: {e}")
            return Response({'error': str(e)}, status=500)


class AddProductView(APIView):
    """POST /api/rag/product/ - add a single product to FAISS (called by product-service)"""

    def post(self, request):
        try:
            product_id = request.data.get('id') or request.data.get('product_id') or request.data.get('book_id')
            if product_id is None:
                return Response({'error': 'id field required'}, status=400)

            vector_store.add_book(
                book_id=int(product_id),
                title=request.data.get('title', ''),
                author=request.data.get('author', ''),
                description=request.data.get('description', ''),
                book_type=request.data.get('book_type_key') or request.data.get('book_type', 'fiction'),
                category=request.data.get('category_name') or request.data.get('category', ''),
                price=float(request.data.get('price', 0)),
                attributes=request.data.get('attributes', {}),
                is_active=request.data.get('is_active', True),
            )
            return Response({'status': 'added', 'id': int(product_id)})
        except Exception as e:
            logger.error(f"AddProduct error: {e}")
            return Response({'error': str(e)}, status=400)


class SearchView(APIView):
    """GET /api/rag/search/?q=query - semantic search books"""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        k = int(request.query_params.get('k', 10))

        if not query:
            return Response({'error': 'q parameter required'}, status=400)

        results = vector_store.search(query, k=k)
        return Response({'results': results, 'query': query, 'count': len(results)})


class VectorStoreStatsView(APIView):
    """GET /api/rag/stats/ - FAISS index statistics"""

    def get(self, request):
        return Response(vector_store.get_stats())
