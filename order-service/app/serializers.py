from rest_framework import serializers
from .models import Order, OrderItem, Invoice, Discount, OrderStatusHistory, OrderReturn


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'book_id', 'quantity', 'price', 'subtotal']


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'amount', 'created_at']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = '__all__'


class OrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReturn
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    invoice = InvoiceSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_id', 'staff_id', 'discount_id',
            'total_amount', 'discount_amount', 'final_amount',
            'status', 'created_at', 'updated_at', 'items', 'invoice'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating orders"""
    customer_id = serializers.IntegerField()
    discount_code = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(
        choices=['cash', 'credit_card', 'debit_card', 'paypal', 'bank_transfer', 'cash_on_delivery'],
        default='cash'
    )
    shipping_method = serializers.ChoiceField(
        choices=['standard', 'express', 'overnight'],
        default='standard'
    )
    shipping_address = serializers.CharField()


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['id', 'code', 'description', 'discount_percent', 'valid_from', 'valid_to', 'is_active']
