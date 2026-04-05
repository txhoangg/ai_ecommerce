from django.db import models


class Rating(models.Model):
    """Book rating - Review bounded context"""
    customer_id = models.IntegerField()  # Reference to customer-service
    book_id = models.IntegerField()  # Reference to book-service
    score = models.FloatField()  # Rating score (e.g., 1-5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer {self.customer_id} - Book {self.book_id} - {self.score}"

    class Meta:
        db_table = 'rating'
        unique_together = ('customer_id', 'book_id')  # One rating per customer per book
        ordering = ['-created_at']


class Review(models.Model):
    """Book review with text comment"""
    customer_id = models.IntegerField()  # Reference to customer-service
    book_id = models.IntegerField()  # Reference to book-service
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by Customer {self.customer_id} on Book {self.book_id}"

    class Meta:
        db_table = 'review'
        unique_together = ('customer_id', 'book_id')  # One review per customer per book
        ordering = ['-created_at']
