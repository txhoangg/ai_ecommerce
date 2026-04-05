from rest_framework import serializers
from .models import (
    Book, Author, BookAuthor, BookFormat, BookImage, 
    BookTag, BookInventoryHistory
)


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookAuthor
        fields = '__all__'


class BookFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookFormat
        fields = '__all__'


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = '__all__'


class BookTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookTag
        fields = '__all__'


class BookInventoryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookInventoryHistory
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'price', 'stock', 'description', 'isbn',
            'category_id', 'publisher_id', 'book_series_id', 'staff_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'price', 'stock', 'description', 'isbn', 'category_id']


class BookStockUpdateSerializer(serializers.Serializer):
    """Serializer for updating book stock"""
    quantity = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['add', 'subtract', 'set'])
