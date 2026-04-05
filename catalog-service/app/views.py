from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Publisher, BookSeries
from .serializers import CategorySerializer, PublisherSerializer, BookSeriesSerializer


class CategoryListCreate(APIView):
    """
    GET: List all categories
    POST: Create new category
    """
    
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetail(APIView):
    """
    GET: Retrieve category details
    PUT: Update category
    DELETE: Delete category
    """
    
    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None
    
    def get(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    
    def put(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublisherListCreate(APIView):
    """
    GET: List all publishers
    POST: Create new publisher
    """
    
    def get(self, request):
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublisherDetail(APIView):
    """
    GET: Retrieve publisher details
    PUT: Update publisher
    DELETE: Delete publisher
    """
    
    def get_object(self, pk):
        try:
            return Publisher.objects.get(pk=pk)
        except Publisher.DoesNotExist:
            return None
    
    def get(self, request, pk):
        publisher = self.get_object(pk)
        if publisher is None:
            return Response({'error': 'Publisher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PublisherSerializer(publisher)
        return Response(serializer.data)
    
    def put(self, request, pk):
        publisher = self.get_object(pk)
        if publisher is None:
            return Response({'error': 'Publisher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PublisherSerializer(publisher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        publisher = self.get_object(pk)
        if publisher is None:
            return Response({'error': 'Publisher not found'}, status=status.HTTP_404_NOT_FOUND)
        
        publisher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookSeriesListCreate(APIView):
    """
    GET: List all book series
    POST: Create new book series
    """
    
    def get(self, request):
        series = BookSeries.objects.all()
        serializer = BookSeriesSerializer(series, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = BookSeriesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookSeriesDetail(APIView):
    """
    GET: Retrieve book series details
    PUT: Update book series
    DELETE: Delete book series
    """
    
    def get_object(self, pk):
        try:
            return BookSeries.objects.get(pk=pk)
        except BookSeries.DoesNotExist:
            return None
    
    def get(self, request, pk):
        series = self.get_object(pk)
        if series is None:
            return Response({'error': 'Book series not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSeriesSerializer(series)
        return Response(serializer.data)
    
    def put(self, request, pk):
        series = self.get_object(pk)
        if series is None:
            return Response({'error': 'Book series not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BookSeriesSerializer(series, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        series = self.get_object(pk)
        if series is None:
            return Response({'error': 'Book series not found'}, status=status.HTTP_404_NOT_FOUND)
        
        series.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
