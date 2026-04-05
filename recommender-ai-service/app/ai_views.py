from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.conf import settings
import requests
import uuid

from .models import ChatSession, ChatMessage
from .ai.knowledge_base import KnowledgeBase
from .ai.rag_engine import RAGEngine
from .ai.ncf_model import BehaviorModelManager

# Singletons (init once)
_kb = None
_rag = None
_model_manager = None

def get_kb():
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb

def get_rag():
    global _rag
    if _rag is None:
        _rag = RAGEngine(get_kb())
    return _rag

def get_model_manager():
    global _model_manager
    if _model_manager is None:
        _model_manager = BehaviorModelManager()
    return _model_manager


class KBBuildView(APIView):
    """POST: Build knowledge base from book-service data"""
    def post(self, request):
        try:
            resp = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/", timeout=10)
            if resp.status_code != 200:
                return Response({'error': 'Cannot fetch books'}, status=503)
            books = resp.json()
            kb = get_kb()
            kb.build_from_books(books)
            faq_count = kb.build_service_faq()
            return Response({
                'message': f'KB built with {len(books)} books + {faq_count} service FAQ entries',
                'books': len(books),
                'faq_entries': faq_count,
                'stats': kb.get_stats()
            })
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class KBQueryView(APIView):
    """POST: Query knowledge base"""
    def post(self, request):
        query = request.data.get('query', '')
        if not query:
            return Response({'error': 'query required'}, status=400)
        n = int(request.data.get('n_results', 5))
        try:
            results = get_kb().query(query, n_results=n)
            return Response({'query': query, 'results': results, 'count': len(results)})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class KBStatsView(APIView):
    """GET: Knowledge base stats"""
    def get(self, request):
        try:
            return Response(get_kb().get_stats())
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class ChatView(APIView):
    """POST: Chat with RAG engine — open to all users (logged in or not)"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        session_id = request.data.get('session_id') or str(uuid.uuid4())
        customer_id = request.data.get('customer_id')
        message = request.data.get('message', '').strip()
        if not message:
            return Response({'error': 'message required'}, status=400)

        # Get or create session
        session, _ = ChatSession.objects.get_or_create(
            session_id=session_id,
            defaults={'customer_id': customer_id}
        )

        # Save user message
        ChatMessage.objects.create(session=session, role='user', content=message)

        # Build history
        history = [
            {'role': m.role, 'content': m.content}
            for m in session.messages.all()
        ]

        # Generate response
        try:
            result = get_rag().chat(history, customer_id=customer_id)
            response_text = result['response']
        except Exception as e:
            response_text = f"Xin lỗi, tôi đang gặp sự cố kỹ thuật. Vui lòng thử lại. ({str(e)})"
            result = {'sources': [], 'retrieved_count': 0}

        # Save assistant message
        ChatMessage.objects.create(session=session, role='assistant', content=response_text)

        return Response({
            'session_id': session_id,
            'message': message,
            'response': response_text,
            'sources': result.get('sources', []),
            'retrieved_count': result.get('retrieved_count', 0),
            'personalized': result.get('personalized', False),
        })


class ChatHistoryView(APIView):
    """GET: Get chat history for a session — open to all users"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = [
                {'role': m.role, 'content': m.content, 'created_at': m.created_at}
                for m in session.messages.all()
            ]
            return Response({'session_id': session_id, 'messages': messages})
        except ChatSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=404)


class BehaviorModelTrainView(APIView):
    """POST: Train NCF model from order + rating data"""
    def post(self, request):
        interactions = []
        try:
            # Get ratings
            resp = requests.get(f"{settings.COMMENT_RATE_SERVICE_URL}/api/ratings/", timeout=10)
            if resp.status_code == 200:
                for r in resp.json():
                    interactions.append({
                        'customer_id': r['customer_id'],
                        'book_id': r['book_id'],
                        'score': float(r['score']) / 5.0  # normalize to 0-1
                    })
        except Exception:
            pass

        try:
            # Get purchase history
            resp = requests.get(f"{settings.ORDER_SERVICE_URL}/api/orders/", timeout=10)
            if resp.status_code == 200:
                for order in resp.json():
                    for item in order.get('items', []):
                        interactions.append({
                            'customer_id': order['customer_id'],
                            'book_id': item['book_id'],
                            'score': 1.0  # purchased = implicit positive
                        })
        except Exception:
            pass

        if not interactions:
            return Response({'error': 'No training data available'}, status=400)

        try:
            mgr = get_model_manager()
            result = mgr.train(interactions)
            return Response({'message': 'Model trained successfully', 'details': result})
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class BehaviorModelRecommendView(APIView):
    """GET: Get NCF-based recommendations for a customer"""
    def get(self, request, customer_id):
        limit = int(request.query_params.get('limit', 10))
        mgr = get_model_manager()
        if not mgr.is_trained():
            return Response({'error': 'Model not trained yet. Call /api/ai/model/train/ first.'}, status=400)

        # Get all books
        try:
            resp = requests.get(f"{settings.BOOK_SERVICE_URL}/api/books/", timeout=10)
            if resp.status_code != 200:
                return Response({'error': 'Cannot fetch books'}, status=503)
            all_books = resp.json()
        except Exception as e:
            return Response({'error': str(e)}, status=503)

        # Collect books already purchased or rated by this customer — filter these out
        seen_book_ids = set()
        try:
            r = requests.get(f"{settings.ORDER_SERVICE_URL}/api/orders/", params={'customer_id': customer_id}, timeout=5)
            if r.status_code == 200:
                for order in r.json():
                    for item in order.get('items', []):
                        seen_book_ids.add(item['book_id'])
        except Exception:
            pass
        try:
            r = requests.get(f"{settings.COMMENT_RATE_SERVICE_URL}/api/ratings/customer/{customer_id}/", timeout=5)
            if r.status_code == 200:
                for rating in r.json():
                    seen_book_ids.add(rating['book_id'])
        except Exception:
            pass

        book_ids = [b['id'] for b in all_books if b['id'] not in seen_book_ids]
        scores = mgr.predict(customer_id, book_ids)

        # Sort and take top-N
        sorted_books = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        books_map = {b['id']: b for b in all_books}

        results = []
        for book_id, score in sorted_books:
            if book_id in books_map:
                results.append({
                    'book': books_map[book_id],
                    'score': round(score * 100, 2),
                    'reason': 'Deep learning behavior model (NCF)'
                })

        return Response({'customer_id': customer_id, 'recommendations': results, 'model': 'NCF', 'filtered_seen': len(seen_book_ids)})


class AIStatusView(APIView):
    """GET: Overall AI system status"""
    def get(self, request):
        kb = get_kb()
        mgr = get_model_manager()
        return Response({
            'knowledge_base': kb.get_stats(),
            'behavior_model': {
                'trained': mgr.is_trained(),
                'model_type': 'Neural Collaborative Filtering (NCF)'
            },
            'rag_engine': {'status': 'ready'},
            'components': ['NCF Model', 'Knowledge Base (ChromaDB)', 'RAG Engine']
        })
