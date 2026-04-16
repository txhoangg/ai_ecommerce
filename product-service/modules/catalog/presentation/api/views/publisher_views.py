import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from modules.catalog.infrastructure.models import PublisherModel
from modules.catalog.presentation.api.serializers.publisher_serializers import (
    PublisherSerializer, PublisherCreateSerializer
)

logger = logging.getLogger(__name__)


class PublisherListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        search = request.query_params.get('search', '')
        qs = PublisherModel.objects.all()
        if search:
            qs = qs.filter(name__icontains=search)
        serializer = PublisherSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PublisherCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        publisher = PublisherModel(
            name=data['name'],
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            website=data.get('website', ''),
        )
        publisher.save()
        return Response(
            PublisherSerializer(publisher).data,
            status=status.HTTP_201_CREATED
        )


class PublisherDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, publisher_id):
        try:
            publisher = PublisherModel.objects.get(id=publisher_id)
            return Response(PublisherSerializer(publisher).data)
        except PublisherModel.DoesNotExist:
            return Response(
                {'error': f'Publisher {publisher_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, publisher_id):
        try:
            publisher = PublisherModel.objects.get(id=publisher_id)
        except PublisherModel.DoesNotExist:
            return Response(
                {'error': f'Publisher {publisher_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PublisherCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        for field, value in data.items():
            setattr(publisher, field, value)
        publisher.save()
        return Response(PublisherSerializer(publisher).data)

    def delete(self, request, publisher_id):
        try:
            publisher = PublisherModel.objects.get(id=publisher_id)
            publisher.delete()
            return Response(
                {'message': f'Publisher {publisher_id} deleted'},
                status=status.HTTP_200_OK
            )
        except PublisherModel.DoesNotExist:
            return Response(
                {'error': f'Publisher {publisher_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
