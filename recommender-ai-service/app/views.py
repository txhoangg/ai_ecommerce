from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BookRecommendation, RecommendationLog
from .serializers import BookRecommendationSerializer, GenerateRecommendationSerializer
import requests
from django.conf import settings
from collections import defaultdict
import time


class RecommendationList(APIView):
    """
    GET: Get recommendations for a customer
    """
    
    def get(self, request, customer_id):
        recommendations = BookRecommendation.objects.filter(customer_id=customer_id)
        
        # Get book details from book-service
        book_ids = [rec.book_id for rec in recommendations]
        books_data = {}
        
        if book_ids:
            try:
                books_response = requests.get(
                    f"{settings.BOOK_SERVICE_URL}/api/books/",
                    timeout=5
                )
                if books_response.status_code == 200:
                    all_books = books_response.json()
                    books_data = {book['id']: book for book in all_books if book['id'] in book_ids}
            except requests.exceptions.RequestException:
                pass
        
        # Combine recommendation with book data
        results = []
        for rec in recommendations:
            rec_data = BookRecommendationSerializer(rec).data
            if rec.book_id in books_data:
                rec_data['book'] = books_data[rec.book_id]
            results.append(rec_data)
        
        return Response(results)


class GenerateRecommendations(APIView):
    """
    POST: Generate recommendations for a customer
    Algorithm:
    1. Get customer's purchase history
    2. Get customer's ratings
    3. Find similar customers (collaborative filtering)
    4. Recommend books from same categories
    5. Recommend popular books
    """
    
    def post(self, request):
        serializer = GenerateRecommendationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        customer_id = serializer.validated_data['customer_id']
        limit = serializer.validated_data['limit']
        
        start_time = time.time()
        
        # Get customer's purchase history from order-service
        purchased_book_ids = set()
        try:
            orders_response = requests.get(
                f"{settings.ORDER_SERVICE_URL}/api/orders/",
                params={'customer_id': customer_id},
                timeout=5
            )
            if orders_response.status_code == 200:
                orders = orders_response.json()
                for order in orders:
                    for item in order.get('items', []):
                        purchased_book_ids.add(item['book_id'])
        except requests.exceptions.RequestException:
            pass
        
        # Get customer's ratings from comment-rate-service
        rated_book_ids = set()
        high_rated_book_ids = set()
        try:
            ratings_response = requests.get(
                f"{settings.COMMENT_RATE_SERVICE_URL}/api/ratings/customer/{customer_id}/",
                timeout=5
            )
            if ratings_response.status_code == 200:
                ratings = ratings_response.json()
                for rating in ratings:
                    rated_book_ids.add(rating['book_id'])
                    if rating['score'] >= 4.0:
                        high_rated_book_ids.add(rating['book_id'])
        except requests.exceptions.RequestException:
            pass
        
        # Get all books from book-service
        all_books = []
        try:
            books_response = requests.get(
                f"{settings.BOOK_SERVICE_URL}/api/books/",
                timeout=5
            )
            if books_response.status_code == 200:
                all_books = books_response.json()
        except requests.exceptions.RequestException:
            pass
        
        # Get categories from purchased/high-rated books
        preferred_categories = set()
        preferred_authors = set()
        books_by_id = {book['id']: book for book in all_books}
        
        for book_id in purchased_book_ids.union(high_rated_book_ids):
            if book_id in books_by_id:
                book = books_by_id[book_id]
                if book.get('category_id'):
                    preferred_categories.add(book['category_id'])
                if book.get('author'):
                    preferred_authors.add(book['author'])
        
        # Generate recommendations
        recommendations = []
        
        # Strategy 1: Books from preferred categories (not purchased/rated)
        for book in all_books:
            if book['id'] not in purchased_book_ids and book['id'] not in rated_book_ids:
                score = 0
                reason = []
                
                # Same category
                if book.get('category_id') in preferred_categories:
                    score += 40
                    reason.append("cùng thể loại yêu thích")
                
                # Same author
                if book.get('author') in preferred_authors:
                    score += 30
                    reason.append("cùng tác giả")
                
                # High average rating
                if book.get('average_rating') and book['average_rating'] >= 4.0:
                    score += 20
                    reason.append("đánh giá cao")
                
                # In stock
                if book.get('stock', 0) > 0:
                    score += 10
                
                if score > 0:
                    recommendations.append({
                        'book_id': book['id'],
                        'score': score,
                        'reason': ', '.join(reason) if reason else 'gợi ý cho bạn'
                    })
        
        # Strategy 2: Popular books only if customer has some history
        has_history = bool(purchased_book_ids or rated_book_ids)
        if has_history and len(recommendations) < limit:
            for book in all_books:
                if book['id'] not in purchased_book_ids and book['id'] not in rated_book_ids:
                    if not any(r['book_id'] == book['id'] for r in recommendations):
                        score = 0
                        if book.get('average_rating'):
                            score = book['average_rating'] * 10
                        if book.get('stock', 0) > 0:
                            score += 5

                        if score > 0:
                            recommendations.append({
                                'book_id': book['id'],
                                'score': score,
                                'reason': 'sách phổ biến'
                            })
        
        # Sort by score and limit
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        recommendations = recommendations[:limit]
        
        # Save recommendations to database
        BookRecommendation.objects.filter(customer_id=customer_id).delete()
        
        for rec in recommendations:
            BookRecommendation.objects.create(
                customer_id=customer_id,
                book_id=rec['book_id'],
                score=rec['score'],
                reason=rec['reason']
            )
        
        # Log recommendation generation
        execution_time = time.time() - start_time
        RecommendationLog.objects.create(
            customer_id=customer_id,
            algorithm='hybrid_collaborative_content',
            books_count=len(recommendations),
            execution_time=execution_time
        )
        
        return Response({
            'customer_id': customer_id,
            'recommendations_count': len(recommendations),
            'execution_time': execution_time,
            'recommendations': recommendations
        }, status=status.HTTP_201_CREATED)


class PopularBooks(APIView):
    """
    GET: Get popular books based on ratings and purchases
    """
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 12))
        
        # Get all ratings from comment-rate-service
        book_ratings = defaultdict(list)
        try:
            ratings_response = requests.get(
                f"{settings.COMMENT_RATE_SERVICE_URL}/api/ratings/",
                timeout=5
            )
            if ratings_response.status_code == 200:
                ratings = ratings_response.json()
                for rating in ratings:
                    book_ratings[rating['book_id']].append(rating['score'])
        except requests.exceptions.RequestException:
            pass
        
        # Calculate average ratings
        book_scores = []
        for book_id, scores in book_ratings.items():
            avg_score = sum(scores) / len(scores)
            book_scores.append({
                'book_id': book_id,
                'average_rating': avg_score,
                'rating_count': len(scores)
            })
        
        # Sort by rating and count
        book_scores.sort(key=lambda x: (x['average_rating'], x['rating_count']), reverse=True)
        book_scores = book_scores[:limit]
        
        # Get book details
        book_ids = [b['book_id'] for b in book_scores]
        books_data = []
        
        if book_ids:
            try:
                books_response = requests.get(
                    f"{settings.BOOK_SERVICE_URL}/api/books/",
                    timeout=5
                )
                if books_response.status_code == 200:
                    all_books = books_response.json()
                    books_dict = {book['id']: book for book in all_books}
                    
                    for score_data in book_scores:
                        book_id = score_data['book_id']
                        if book_id in books_dict:
                            book = books_dict[book_id]
                            book['average_rating'] = score_data['average_rating']
                            book['rating_count'] = score_data['rating_count']
                            books_data.append(book)
            except requests.exceptions.RequestException:
                pass
        
        return Response(books_data)
