from rest_framework import serializers
from .models import (
    Customer, Address, Membership, Notification, Wishlist, WishlistItem,
    CustomerPreference, LoginHistory, CustomerSupport, CustomerReview
)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = '__all__'


class CustomerPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerPreference
        fields = '__all__'


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = '__all__'


class CustomerSupportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerSupport
        fields = '__all__'


class CustomerReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerReview
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    membership = MembershipSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'password', 'created_at', 'addresses', 'membership']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create customer with hashed password and default membership"""
        customer = Customer(
            name=validated_data['name'],
            email=validated_data['email']
        )
        customer.set_password(validated_data['password'])
        customer.save()
        
        # Create default membership
        Membership.objects.create(
            customer=customer,
            level='bronze',
            point=0
        )
        
        return customer


class CustomerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
