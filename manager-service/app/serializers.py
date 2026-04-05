from rest_framework import serializers
from .models import Manager, Report, ManagerActivity


class ManagerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Manager
        fields = ['id', 'name', 'email', 'password', 'phone', 'department', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        manager = Manager(**validated_data)
        if password:
            manager.set_password(password)
        manager.save()
        return manager


class ManagerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'manager_id', 'report_type', 'title', 'content', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['id', 'created_at']


class ManagerActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerActivity
        fields = ['id', 'manager_id', 'action', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class SalesReportRequestSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
