from rest_framework import serializers
from .models import Staff, InventoryLog


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'name', 'email', 'password', 'role', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create staff with hashed password"""
        staff = Staff(
            name=validated_data['name'],
            email=validated_data['email'],
            role=validated_data.get('role', 'staff')
        )
        staff.set_password(validated_data['password'])
        staff.save()
        return staff


class StaffLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class InventoryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLog
        fields = ['id', 'staff_id', 'book_id', 'action', 'quantity', 'created_at']
