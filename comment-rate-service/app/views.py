from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Rating, Review
from .serializers import RatingSerializer, ReviewSerializer
from django.db.models import Avg


class RatingCreate(APIView):
    """
    GET: List all ratings
    POST: Create or update rating
    """

    def get(self, request):
        ratings = Rating.objects.all()
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    def post(self, request):
        customer_id = request.data.get('customer_id')
        book_id = request.data.get('book_id')
        score = request.data.get('score')
        
        if not customer_id or not book_id or score is None:
            return Response({
                'error': 'customer_id, book_id, and score required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate score range
        try:
            score = float(score)
            if score < 1 or score > 5:
                return Response({
                    'error': 'Score must be between 1 and 5'
                }, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({
                'error': 'Invalid score value'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update rating
        rating, created = Rating.objects.update_or_create(
            customer_id=customer_id,
            book_id=book_id,
            defaults={'score': score}
        )
        
        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class RatingByBook(APIView):
    """
    GET: Get all ratings for a book
    """
    
    def get(self, request, book_id):
        ratings = Rating.objects.filter(book_id=book_id)
        
        # Calculate average
        avg_rating = ratings.aggregate(Avg('score'))['score__avg']
        
        serializer = RatingSerializer(ratings, many=True)
        return Response({
            'ratings': serializer.data,
            'average': round(avg_rating, 2) if avg_rating else None,
            'count': ratings.count()
        })


class RatingByCustomer(APIView):
    """
    GET: Get all ratings by a customer
    """
    
    def get(self, request, customer_id):
        ratings = Rating.objects.filter(customer_id=customer_id)
        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)


class ReviewCreate(APIView):
    """
    POST: Create or update review
    """
    
    def post(self, request):
        customer_id = request.data.get('customer_id')
        book_id = request.data.get('book_id')
        comment = request.data.get('comment')
        
        if not customer_id or not book_id or not comment:
            return Response({
                'error': 'customer_id, book_id, and comment required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create or update review
        review, created = Review.objects.update_or_create(
            customer_id=customer_id,
            book_id=book_id,
            defaults={'comment': comment}
        )
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ReviewByBook(APIView):
    """
    GET: Get all reviews for a book
    """
    
    def get(self, request, book_id):
        reviews = Review.objects.filter(book_id=book_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response({
            'reviews': serializer.data,
            'count': reviews.count()
        })


class ReviewByCustomer(APIView):
    """
    GET: Get all reviews by a customer
    """
    
    def get(self, request, customer_id):
        reviews = Review.objects.filter(customer_id=customer_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class ReviewDetail(APIView):
    """
    GET: Get review details
    PUT: Update review
    DELETE: Delete review
    """
    
    def get(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
        
        comment = request.data.get('comment')
        if comment:
            review.comment = comment
            review.save()
        
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Review.DoesNotExist:
            return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)
