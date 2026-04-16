from django.db import models
from .book_type_model import BookTypeModel
from .category_model import CategoryModel
from .publisher_model import PublisherModel


class BookModel(models.Model):
    title = models.CharField(max_length=500)
    book_type = models.ForeignKey(
        BookTypeModel,
        on_delete=models.PROTECT,
        related_name='books'
    )
    category = models.ForeignKey(
        CategoryModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='books'
    )
    publisher = models.ForeignKey(
        PublisherModel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='books'
    )
    author = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    isbn = models.CharField(max_length=20, blank=True)
    image_url = models.URLField(blank=True, max_length=1000)
    attributes = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['book_type'], name='books_book_type_idx'),
            models.Index(fields=['category'], name='books_category_idx'),
            models.Index(fields=['is_active'], name='books_is_active_idx'),
            models.Index(fields=['price'], name='books_price_idx'),
        ]

    def __str__(self):
        return self.title
