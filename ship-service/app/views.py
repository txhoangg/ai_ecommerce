from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Shipping, ShippingCarrier, ShippingTracking
from .serializers import ShippingSerializer, ShippingCarrierSerializer
from decimal import Decimal
import uuid


class ShippingCreate(APIView):
    """
    POST: Create new shipping (called by order-service)
    """
    
    def post(self, request):
        order_id = request.data.get('order_id')
        customer_id = request.data.get('customer_id')
        method = request.data.get('method', 'standard')
        address = request.data.get('address')
        
        if not order_id or not customer_id or not address:
            return Response({
                'error': 'order_id, customer_id, and address required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate shipping fee based on method
        fee_map = {
            'standard': Decimal('5.00'),
            'express': Decimal('15.00'),
            'overnight': Decimal('25.00')
        }
        fee = fee_map.get(method, Decimal('5.00'))
        
        # Get default carrier (or create one if none exists)
        carrier = ShippingCarrier.objects.first()
        if not carrier:
            carrier = ShippingCarrier.objects.create(
                name='Default Carrier',
                phone='1-800-SHIP',
                email='shipping@bookstore.com',
                base_fee=Decimal('5.00')
            )
        
        # Create shipping
        shipping = Shipping.objects.create(
            order_id=order_id,
            customer_id=customer_id,
            carrier=carrier,
            tracking_number=f"TRACK-{uuid.uuid4().hex[:12].upper()}",
            method=method,
            fee=fee,
            address=address,
            status='pending'
        )
        
        # Create initial tracking entry
        ShippingTracking.objects.create(
            shipping=shipping,
            status='pending',
            location='Warehouse',
            message='Shipment created and pending processing'
        )
        
        serializer = ShippingSerializer(shipping)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShippingDetail(APIView):
    """
    GET: Retrieve shipping details
    PUT: Update shipping status
    """
    
    def get(self, request, pk):
        try:
            shipping = Shipping.objects.get(pk=pk)
        except Shipping.DoesNotExist:
            return Response({'error': 'Shipping not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ShippingSerializer(shipping)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            shipping = Shipping.objects.get(pk=pk)
        except Shipping.DoesNotExist:
            return Response({'error': 'Shipping not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        location = request.data.get('location', 'Unknown')
        message = request.data.get('message', '')
        
        if new_status and new_status in dict(Shipping.STATUS_CHOICES):
            shipping.status = new_status
            shipping.save()
            
            # Add tracking entry
            ShippingTracking.objects.create(
                shipping=shipping,
                status=new_status,
                location=location,
                message=message or f'Status updated to {new_status}'
            )
        
        serializer = ShippingSerializer(shipping)
        return Response(serializer.data)


class ShippingByOrder(APIView):
    """
    GET: Get shipping by order_id
    """
    
    def get(self, request, order_id):
        try:
            shipping = Shipping.objects.get(order_id=order_id)
            serializer = ShippingSerializer(shipping)
            return Response(serializer.data)
        except Shipping.DoesNotExist:
            return Response({'error': 'Shipping not found'}, status=status.HTTP_404_NOT_FOUND)


class ShippingTrack(APIView):
    """
    GET: Track shipment by tracking number
    """
    
    def get(self, request, tracking_number):
        try:
            shipping = Shipping.objects.get(tracking_number=tracking_number)
            serializer = ShippingSerializer(shipping)
            return Response(serializer.data)
        except Shipping.DoesNotExist:
            return Response({'error': 'Tracking number not found'}, status=status.HTTP_404_NOT_FOUND)


class ShippingList(APIView):
    """
    GET: List all shipments
    """
    
    def get(self, request):
        shipments = Shipping.objects.all()
        
        # Filter by customer
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            shipments = shipments.filter(customer_id=customer_id)
        
        serializer = ShippingSerializer(shipments, many=True)
        return Response(serializer.data)


class CarrierListCreate(APIView):
    """
    GET: List all carriers
    POST: Create new carrier
    """
    
    def get(self, request):
        carriers = ShippingCarrier.objects.all()
        serializer = ShippingCarrierSerializer(carriers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ShippingCarrierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
