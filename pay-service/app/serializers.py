from rest_framework import serializers
from .models import Payment, PaymentTransaction


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ['id', 'transaction_type', 'amount', 'status', 'message', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    transactions = PaymentTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order_id', 'transaction_id', 'method', 'amount',
            'status', 'created_at', 'updated_at', 'transactions'
        ]
        read_only_fields = ['transaction_id', 'created_at', 'updated_at']
