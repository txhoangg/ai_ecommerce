from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem, Invoice, Discount
from .serializers import OrderSerializer, CreateOrderSerializer, DiscountSerializer
import requests
from django.conf import settings
from decimal import Decimal
from datetime import datetime, date
import uuid
from .rabbitmq import publish_command


class OrderCreate(APIView):
    """
    POST: Create new order and initiate Saga Pattern via RabbitMQ
    """
    
    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        customer_id = serializer.validated_data['customer_id']
        discount_code = serializer.validated_data.get('discount_code', '')
        payment_method = serializer.validated_data['payment_method']
        shipping_method = serializer.validated_data['shipping_method']
        shipping_address = serializer.validated_data['shipping_address']
        
        # 1. Tương tác đồng bộ để lấy giỏ hàng (Cart)
        try:
            cart_response = requests.get(
                f"{settings.CART_SERVICE_URL}/api/carts/{customer_id}/",
                timeout=5
            )
            if cart_response.status_code != 200:
                return Response({'error': 'Failed to get cart'}, status=status.HTTP_400_BAD_REQUEST)
            
            cart_data = cart_response.json()
            cart_items = cart_data.get('items', [])
            
            if not cart_items:
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Cart service unavailable: {str(e)}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # 2. Xử lý tính tiền
        total_amount = Decimal(str(cart_data.get('total', 0)))
        discount_amount = Decimal('0')
        discount_id = None
        
        if discount_code:
            try:
                discount = Discount.objects.get(code=discount_code, is_active=True)
                today = date.today()
                if discount.valid_from <= today <= discount.valid_to:
                    discount_amount = total_amount * (discount.discount_percent / Decimal('100'))
                    discount_id = discount.id
            except Discount.DoesNotExist:
                pass
        
        final_amount = total_amount - discount_amount
        
        # 3. Tạo Order (Trạng thái Pending để Saga quản lý)
        order = Order.objects.create(
            customer_id=customer_id,
            discount_id=discount_id,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            status='pending'
        )
        
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                book_id=cart_item['book_id'],
                quantity=cart_item['quantity'],
                price=Decimal(str(cart_item['price']))
            )
            
        # NOTE: Cart is NOT cleared here.
        # Cart sẽ được xóa bởi order orchestrator (consumer) SAU KHI Saga hoàn tất thành công.
        # Nếu payment/inventory/shipping fail → Saga rollback → cart vẫn còn nguyên cho customer.

        # 4. Kích hoạt Saga Pattern: Gửi event Payment Processing qua RabbitMQ
        payload = {
            'order_id': order.id,
            'customer_id': customer_id,
            'amount': float(final_amount),
            'method': payment_method,
            'ship_method': shipping_method,
            'address': shipping_address,
            'items': cart_items
        }
        
        # Dispatch event cho Pay Service
        published = publish_command('order.created', payload)
        
        if not published:
            # Fallback nếu broker chết ngay khi submit
            order.status = 'cancelled'
            order.save()
            return Response({'error': 'Message broker unavailable, order cancelled'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 5. Trả lời ngay cho Frontend (Async)
        order_serializer = OrderSerializer(order)
        return Response({
            'message': 'Order has been placed and is processing in background.',
            'order': order_serializer.data,
            'status': 'Processing'
        }, status=status.HTTP_201_CREATED)


class OrderDetail(APIView):
    """
    GET: Retrieve order details
    PUT: Update order status
    """
    
    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class OrderList(APIView):
    """
    GET: List all orders (with optional customer filter)
    """
    
    def get(self, request):
        orders = Order.objects.all()
        
        # Filter by customer
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            orders = orders.filter(customer_id=customer_id)
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class DiscountListCreate(APIView):
    """
    GET: List all discounts
    POST: Create new discount
    """
    
    def get(self, request):
        discounts = Discount.objects.all()
        serializer = DiscountSerializer(discounts, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = DiscountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DiscountValidate(APIView):
    """
    POST: Validate discount code
    """
    
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'error': 'code required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            discount = Discount.objects.get(code=code, is_active=True)
            today = date.today()
            
            if discount.valid_from <= today <= discount.valid_to:
                serializer = DiscountSerializer(discount)
                return Response({
                    'valid': True,
                    'discount': serializer.data
                })
            else:
                return Response({
                    'valid': False,
                    'error': 'Discount code expired'
                })
        except Discount.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid discount code'
            })
