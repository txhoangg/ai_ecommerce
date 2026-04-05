from rest_framework import serializers
from .models import BookRecommendation, RecommendationLog


class BookRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookRecommendation
        fields = ['id', 'customer_id', 'book_id', 'score', 'reason', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class RecommendationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecommendationLog
        fields = ['id', 'customer_id', 'algorithm', 'books_count', 'execution_time', 'created_at']
        read_only_fields = ['id', 'created_at']


class GenerateRecommendationSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=True)
    limit = serializers.IntegerField(default=12, min_value=1, max_value=50)
