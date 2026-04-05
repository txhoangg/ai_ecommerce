from django.db import models


class Category(models.Model):
    """Book category - Catalog bounded context"""
    type = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.type

    class Meta:
        db_table = 'category'
        verbose_name_plural = 'Categories'


class Publisher(models.Model):
    """Publisher model"""
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    address = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'publisher'


class BookSeries(models.Model):
    """Book series"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_books = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'book_series'
        verbose_name_plural = 'Book Series'
