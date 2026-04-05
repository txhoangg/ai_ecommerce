from django.db import models


class Book(models.Model):
    """Book model - Catalog bounded context"""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    
    # Foreign keys stored as IDs (references to other services)
    category_id = models.IntegerField(null=True, blank=True)  # Reference to catalog-service
    publisher_id = models.IntegerField(null=True, blank=True)  # Reference to catalog-service
    book_series_id = models.IntegerField(null=True, blank=True)  # Reference to catalog-service
    staff_id = models.IntegerField(null=True, blank=True)  # Reference to staff-service
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'book'
        ordering = ['-created_at']


class Author(models.Model):
    """Author model"""
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'author'


class BookAuthor(models.Model):
    """Many-to-many relationship between books and authors"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_authors')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_books')

    class Meta:
        db_table = 'book_author'
        unique_together = ('book', 'author')


class BookFormat(models.Model):
    """Book format (Hardcover, Paperback, eBook, etc.)"""
    FORMAT_CHOICES = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'eBook'),
        ('audiobook', 'Audiobook'),
    ]
    
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='formats')
    format_type = models.CharField(max_length=50, choices=FORMAT_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.book.title} - {self.format_type}"

    class Meta:
        db_table = 'book_format'


class BookImage(models.Model):
    """Book images"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=500)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.book.title}"

    class Meta:
        db_table = 'book_image'


class BookTag(models.Model):
    """Book tags for categorization and search"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='tags')
    tag_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.book.title} - {self.tag_name}"

    class Meta:
        db_table = 'book_tag'


class BookInventoryHistory(models.Model):
    """Book inventory history"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='inventory_history')
    staff_id = models.IntegerField()  # Reference to staff-service
    action = models.CharField(max_length=100)  # 'add', 'remove', 'adjust'
    quantity = models.IntegerField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} - {self.action} - {self.quantity}"

    class Meta:
        db_table = 'book_inventory_history'
        ordering = ['-created_at']
