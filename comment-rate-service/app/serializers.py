from rest_framework import serializers
from .models import Rating, Review


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'customer_id', 'book_id', 'score', 'created_at']
        read_only_fields = ['created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'customer_id', 'book_id', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
