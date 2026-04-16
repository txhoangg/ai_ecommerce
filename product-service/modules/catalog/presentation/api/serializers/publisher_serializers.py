from rest_framework import serializers
from modules.catalog.infrastructure.models import PublisherModel


class PublisherSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = PublisherModel
        fields = [
            'id', 'name', 'email', 'phone',
            'address', 'website', 'books_count', 'created_at'
        ]

    def get_books_count(self, obj) -> int:
        return obj.books.filter(is_active=True).count()


class PublisherCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')
    address = serializers.CharField(required=False, allow_blank=True, default='')
    website = serializers.URLField(required=False, allow_blank=True, default='')
