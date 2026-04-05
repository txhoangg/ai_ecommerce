from django.contrib import admin
from .models import Manager, Report, ManagerActivity


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'email']
    ordering = ['-created_at']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'report_type', 'manager_id', 'start_date', 'end_date', 'created_at']
    list_filter = ['report_type', 'created_at']
    search_fields = ['title', 'content']
    ordering = ['-created_at']


@admin.register(ManagerActivity)
class ManagerActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'manager_id', 'action', 'created_at']
    list_filter = ['created_at']
    search_fields = ['action', 'description']
    ordering = ['-created_at']
