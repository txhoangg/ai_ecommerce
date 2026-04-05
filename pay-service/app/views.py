from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Payment, PaymentTransaction
from .serializers import PaymentSerializer
import uuid


class PaymentCreate(APIView):
    """
    POST: Create new payment (called by order-service)
    """
    
    def post(self, request):
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')
        method = request.data.get('method', 'cash')
        
        if not order_id or not amount:
            return Response({
                'error': 'order_id and amount required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment
        payment = Payment.objects.create(
            order_id=order_id,
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            method=method,
            amount=amount,
            status='pending'
        )
        
        # Simulate payment processing
        # In real system, this would integrate with payment gateway
        if method in ('cash', 'cash_on_delivery'):
            # Cash on delivery - mark as pending
            payment.status = 'pending'
            transaction_status = 'pending'
            message = 'Cash on delivery - payment pending'
        else:
            # Simulate successful payment for other methods
            payment.status = 'completed'
            transaction_status = 'success'
            message = f'Payment processed successfully via {method}'
        
        payment.save()
        
        # Log transaction
        PaymentTransaction.objects.create(
            payment=payment,
            transaction_type='charge',
            amount=amount,
            status=transaction_status,
            message=message
        )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentDetail(APIView):
    """
    GET: Retrieve payment details
    PUT: Update payment status
    """
    
    def get(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
    
    def put(self, request, pk):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if new_status and new_status in dict(Payment.STATUS_CHOICES):
            old_status = payment.status
            payment.status = new_status
            payment.save()
            
            # Log status change
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='status_change',
                amount=payment.amount,
                status=new_status,
                message=f'Status changed from {old_status} to {new_status}'
            )
        
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)


class PaymentByOrder(APIView):
    """
    GET: Get payment by order_id
    """
    
    def get(self, request, order_id):
        try:
            payment = Payment.objects.get(order_id=order_id)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)


class PaymentList(APIView):
    """
    GET: List all payments
    """
    
    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
