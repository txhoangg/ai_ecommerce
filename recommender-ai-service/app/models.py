from django.db import models


class BookRecommendation(models.Model):
    """
    Book recommendation for customers
    Generated based on purchase history, ratings, and collaborative filtering
    """
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    score = models.FloatField(help_text="Recommendation score (0-100)")
    reason = models.CharField(max_length=255, help_text="Reason for recommendation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'book_recommendation'
        ordering = ['-score', '-created_at']
        unique_together = ('customer_id', 'book_id')
    
    def __str__(self):
        return f"Recommend book {self.book_id} to customer {self.customer_id} (score: {self.score})"


class RecommendationLog(models.Model):
    """
    Log of recommendation generation
    """
    customer_id = models.IntegerField()
    algorithm = models.CharField(max_length=100, help_text="Algorithm used")
    books_count = models.IntegerField(help_text="Number of books recommended")
    execution_time = models.FloatField(help_text="Execution time in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendation_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Recommendation for customer {self.customer_id} at {self.created_at}"


class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)
    customer_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chat_session'


class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_message'
        ordering = ['created_at']
