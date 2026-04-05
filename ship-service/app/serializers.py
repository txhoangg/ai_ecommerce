from rest_framework import serializers
from .models import Shipping, ShippingCarrier, ShippingTracking


class ShippingCarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCarrier
        fields = ['id', 'name', 'phone', 'email', 'base_fee']


class ShippingTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingTracking
        fields = ['id', 'status', 'location', 'message', 'created_at']


class ShippingSerializer(serializers.ModelSerializer):
    carrier_details = ShippingCarrierSerializer(source='carrier', read_only=True)
    tracking = ShippingTrackingSerializer(many=True, read_only=True)
    
    class Meta:
        model = Shipping
        fields = [
            'id', 'order_id', 'customer_id', 'carrier', 'carrier_details',
            'tracking_number', 'method', 'fee', 'address', 'status',
            'created_at', 'updated_at', 'tracking'
        ]
        read_only_fields = ['tracking_number', 'created_at', 'updated_at']
