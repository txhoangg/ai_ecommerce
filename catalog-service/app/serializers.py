from rest_framework import serializers
from .models import Category, Publisher, BookSeries


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'type', 'description']


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'phone', 'email', 'address']


class BookSeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSeries
        fields = ['id', 'name', 'description', 'total_books']
