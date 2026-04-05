from django.contrib import admin
from .models import BookRecommendation, RecommendationLog


@admin.register(BookRecommendation)
class BookRecommendationAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id', 'book_id', 'score', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer_id', 'book_id', 'reason']
    ordering = ['-score', '-created_at']


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_id', 'algorithm', 'books_count', 'execution_time', 'created_at']
    list_filter = ['algorithm', 'created_at']
    search_fields = ['customer_id']
    ordering = ['-created_at']
