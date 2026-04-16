from decimal import Decimal
from rest_framework import serializers
from modules.catalog.infrastructure.models import (
    BookModel, BookTypeModel
)


class BookTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookTypeModel
        fields = [
            'id', 'type_key', 'name', 'name_vi',
            'description', 'attribute_schema', 'icon'
        ]


class BookListSerializer(serializers.ModelSerializer):
    book_type_key = serializers.CharField(source='book_type.type_key', read_only=True)
    book_type_name = serializers.CharField(source='book_type.name_vi', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True, allow_null=True)

    class Meta:
        model = BookModel
        fields = [
            'id', 'title', 'author', 'book_type_key', 'book_type_name',
            'category_name', 'publisher_name',
            'price', 'stock', 'isbn', 'image_url',
            'is_active', 'created_at',
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    book_type = BookTypeSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category_id = serializers.IntegerField(source='category.id', read_only=True, allow_null=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True, allow_null=True)
    publisher_id = serializers.IntegerField(source='publisher.id', read_only=True, allow_null=True)

    class Meta:
        model = BookModel
        fields = [
            'id', 'title', 'author', 'book_type',
            'category_id', 'category_name',
            'publisher_id', 'publisher_name',
            'description', 'price', 'stock',
            'isbn', 'image_url', 'attributes',
            'is_active', 'created_at', 'updated_at',
        ]


class BookCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    author = serializers.CharField(max_length=300, required=False, allow_blank=True, default='')
    book_type_key = serializers.CharField(max_length=50)
    description = serializers.CharField(default='', allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0'))
    stock = serializers.IntegerField(min_value=0, default=0)
    isbn = serializers.CharField(max_length=20, default='', allow_blank=True)
    publisher_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True, default='')
    attributes = serializers.DictField(required=False, default=dict)

    def validate_book_type_key(self, value):
        if not BookTypeModel.objects.filter(type_key=value).exists():
            raise serializers.ValidationError(
                f"Book type '{value}' does not exist."
            )
        return value


class BookUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500, required=False)
    author = serializers.CharField(max_length=300, required=False, allow_blank=True)
    book_type_key = serializers.CharField(max_length=50, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        min_value=Decimal('0'), required=False
    )
    stock = serializers.IntegerField(min_value=0, required=False)
    isbn = serializers.CharField(max_length=20, required=False, allow_blank=True)
    publisher_id = serializers.IntegerField(required=False, allow_null=True)
    category_id = serializers.IntegerField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_blank=True)
    attributes = serializers.DictField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate_book_type_key(self, value):
        if not BookTypeModel.objects.filter(type_key=value).exists():
            raise serializers.ValidationError(
                f"Book type '{value}' does not exist."
            )
        return value


class BookStockUpdateSerializer(serializers.Serializer):
    quantity_delta = serializers.IntegerField(
        required=False,
        default=0,
        help_text="Positive to add stock, negative to remove stock"
    )
    stock = serializers.IntegerField(
        required=False, min_value=0,
        help_text="Set absolute stock value (overrides quantity_delta)"
    )
