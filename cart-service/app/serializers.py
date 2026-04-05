from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'book_id', 'quantity', 'price', 'subtotal', 'added_at']
        read_only_fields = ['added_at']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'created_at', 'is_active', 'items', 'total']
        read_only_fields = ['created_at']
    
    def get_total(self, obj):
        return obj.get_total()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
