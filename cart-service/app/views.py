from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddToCartSerializer
import requests
from django.conf import settings
from decimal import Decimal


class CartCreate(APIView):
    """
    POST: Create new cart (called by customer-service)
    """
    
    def post(self, request):
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({'error': 'customer_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if customer already has an active cart
        existing_cart = Cart.objects.filter(customer_id=customer_id, is_active=True).first()
        if existing_cart:
            serializer = CartSerializer(existing_cart)
            return Response(serializer.data)
        
        # Create new cart
        cart = Cart.objects.create(customer_id=customer_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartDetail(APIView):
    """
    GET: View customer's cart
    DELETE: Clear cart
    """
    
    def get(self, request, customer_id):
        try:
            cart = Cart.objects.get(customer_id=customer_id, is_active=True)
        except Cart.DoesNotExist:
            # Auto-create cart if doesn't exist
            cart = Cart.objects.create(customer_id=customer_id)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def delete(self, request, customer_id):
        """Clear all items from cart"""
        try:
            cart = Cart.objects.get(customer_id=customer_id, is_active=True)
            cart.items.all().delete()
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)


class CartItemAdd(APIView):
    """
    POST: Add item to cart
    """
    
    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        customer_id = request.data.get('customer_id')
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']
        
        if not customer_id:
            return Response({'error': 'customer_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(
            customer_id=customer_id,
            is_active=True
        )
        
        # Verify book exists and get price from book-service
        try:
            book_response = requests.get(
                f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/",
                timeout=5
            )
            
            if book_response.status_code == 404:
                return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if book_response.status_code != 200:
                return Response({'error': 'Book service unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            book_data = book_response.json()
            
            book_price = Decimal(str(book_data['price']))
            available_stock = book_data['stock']

        except requests.exceptions.RequestException as e:
            return Response({
                'error': 'Failed to verify book',
                'detail': str(e)
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # Check if item already in cart — must account for existing quantity
        existing_item = CartItem.objects.filter(cart=cart, book_id=book_id).first()
        existing_quantity = existing_item.quantity if existing_item else 0
        total_quantity = existing_quantity + quantity

        if total_quantity > available_stock:
            return Response({
                'error': 'Insufficient stock',
                'available': available_stock,
                'already_in_cart': existing_quantity,
                'requested': quantity,
                'total_would_be': total_quantity,
            }, status=status.HTTP_400_BAD_REQUEST)

        if existing_item:
            existing_item.quantity = total_quantity
            existing_item.save()
            cart_item = existing_item
            item_created = False
        else:
            cart_item = CartItem.objects.create(
                cart=cart, book_id=book_id,
                quantity=quantity, price=book_price
            )
            item_created = True
        
        item_serializer = CartItemSerializer(cart_item)
        return Response(item_serializer.data, status=status.HTTP_201_CREATED)


class CartItemUpdate(APIView):
    """
    PUT: Update cart item quantity
    DELETE: Remove item from cart
    """
    
    def put(self, request, pk):
        try:
            cart_item = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ownership check: verify this item belongs to the requesting customer
        customer_id = request.data.get('customer_id') or request.query_params.get('customer_id')
        if customer_id and str(cart_item.cart.customer_id) != str(customer_id):
            return Response({'error': 'Forbidden: this item does not belong to you'}, status=status.HTTP_403_FORBIDDEN)

        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({'error': 'quantity required'}, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = int(quantity)
        if quantity < 1:
            return Response({'error': 'quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify stock availability
        try:
            book_response = requests.get(
                f"{settings.BOOK_SERVICE_URL}/api/books/{cart_item.book_id}/",
                timeout=5
            )
            
            if book_response.status_code == 200:
                book_data = book_response.json()
                if book_data['stock'] < quantity:
                    return Response({
                        'error': 'Insufficient stock',
                        'available': book_data['stock'],
                        'requested': quantity
                    }, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException:
            pass  # Continue even if book service is down
        
        cart_item.quantity = quantity
        cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        try:
            cart_item = CartItem.objects.get(pk=pk)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ownership check: verify this item belongs to the requesting customer
        customer_id = request.data.get('customer_id') or request.query_params.get('customer_id')
        if customer_id and str(cart_item.cart.customer_id) != str(customer_id):
            return Response({'error': 'Forbidden: this item does not belong to you'}, status=status.HTTP_403_FORBIDDEN)

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartList(APIView):
    """
    GET: List all carts (for admin/debugging)
    """
    
    def get(self, request):
        carts = Cart.objects.all()
        serializer = CartSerializer(carts, many=True)
        return Response(serializer.data)
