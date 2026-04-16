import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from modules.catalog.infrastructure.models import CategoryModel
from modules.catalog.presentation.api.serializers.category_serializers import (
    CategorySerializer, CategoryDetailSerializer, CategoryCreateSerializer
)
from shared.utils import slugify

logger = logging.getLogger(__name__)


class CategoryListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        parent_id = request.query_params.get('parent_id')
        root_only = request.query_params.get('root_only', 'false').lower() == 'true'

        qs = CategoryModel.objects.select_related('parent').prefetch_related('children')

        if root_only:
            qs = qs.filter(parent__isnull=True)
        elif parent_id:
            qs = qs.filter(parent_id=parent_id)

        serializer = CategorySerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategoryCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        slug = data.get('slug') or slugify(data['name'])

        if CategoryModel.objects.filter(slug=slug).exists():
            slug = f"{slug}-{CategoryModel.objects.count()}"

        category = CategoryModel(
            name=data['name'],
            slug=slug,
            description=data.get('description', ''),
        )

        parent_id = data.get('parent_id')
        if parent_id:
            try:
                category.parent = CategoryModel.objects.get(id=parent_id)
            except CategoryModel.DoesNotExist:
                return Response(
                    {'error': f'Parent category {parent_id} not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        category.save()
        return Response(
            CategoryDetailSerializer(category).data,
            status=status.HTTP_201_CREATED
        )


class CategoryDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, category_id):
        try:
            category = CategoryModel.objects.select_related('parent').prefetch_related(
                'children'
            ).get(id=category_id)
            return Response(CategoryDetailSerializer(category).data)
        except CategoryModel.DoesNotExist:
            return Response(
                {'error': f'Category {category_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, category_id):
        try:
            category = CategoryModel.objects.get(id=category_id)
        except CategoryModel.DoesNotExist:
            return Response(
                {'error': f'Category {category_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CategoryCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if 'name' in data:
            category.name = data['name']
        if 'slug' in data and data['slug']:
            category.slug = data['slug']
        if 'description' in data:
            category.description = data['description']
        if 'parent_id' in data:
            if data['parent_id']:
                try:
                    category.parent = CategoryModel.objects.get(id=data['parent_id'])
                except CategoryModel.DoesNotExist:
                    return Response(
                        {'error': f'Parent category {data["parent_id"]} not found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                category.parent = None

        category.save()
        return Response(CategoryDetailSerializer(category).data)

    def delete(self, request, category_id):
        try:
            category = CategoryModel.objects.get(id=category_id)
            category.delete()
            return Response(
                {'message': f'Category {category_id} deleted'},
                status=status.HTTP_200_OK
            )
        except CategoryModel.DoesNotExist:
            return Response(
                {'error': f'Category {category_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
