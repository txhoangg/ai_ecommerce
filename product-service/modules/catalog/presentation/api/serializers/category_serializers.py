from rest_framework import serializers
from modules.catalog.infrastructure.models import CategoryModel


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    children_count = serializers.SerializerMethodField()

    class Meta:
        model = CategoryModel
        fields = [
            'id', 'name', 'slug', 'description',
            'parent', 'parent_name', 'children_count', 'created_at'
        ]

    def get_children_count(self, obj) -> int:
        return obj.children.count()


class CategoryDetailSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    children = serializers.SerializerMethodField()
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = CategoryModel
        fields = [
            'id', 'name', 'slug', 'description',
            'parent', 'parent_name', 'children',
            'books_count', 'created_at'
        ]

    def get_children(self, obj) -> list:
        children = obj.children.all()
        return CategorySerializer(children, many=True).data

    def get_books_count(self, obj) -> int:
        return obj.books.filter(is_active=True).count()


class CategoryCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=200, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_slug(self, value):
        if value and CategoryModel.objects.filter(slug=value).exists():
            raise serializers.ValidationError(f"Slug '{value}' already exists.")
        return value
