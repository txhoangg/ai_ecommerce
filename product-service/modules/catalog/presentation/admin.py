from django.contrib import admin
from modules.catalog.infrastructure.models import (
    BookModel, BookTypeModel, CategoryModel, PublisherModel
)


@admin.register(BookTypeModel)
class BookTypeAdmin(admin.ModelAdmin):
    list_display = ['type_key', 'name_vi', 'name', 'icon', 'created_at']
    search_fields = ['type_key', 'name', 'name_vi']
    readonly_fields = ['created_at']


@admin.register(CategoryModel)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    search_fields = ['name', 'slug']
    list_filter = ['parent']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']


@admin.register(PublisherModel)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'website', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at']


@admin.register(BookModel)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'book_type', 'category', 'publisher',
        'price', 'stock', 'is_active', 'created_at'
    ]
    list_filter = ['book_type', 'category', 'is_active', 'created_at']
    search_fields = ['title', 'isbn', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'stock']
    raw_id_fields = ['category', 'publisher']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'book_type', 'description', 'isbn', 'image_url')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'is_active')
        }),
        ('Relations', {
            'fields': ('category', 'publisher')
        }),
        ('Attributes', {
            'fields': ('attributes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
