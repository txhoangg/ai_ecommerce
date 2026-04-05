from django.db import models
import uuid


class Payment(models.Model):
    """Payment model - Payment bounded context"""
    METHOD_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    order_id = models.IntegerField()  # Reference to order-service
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - Order {self.order_id}"

    class Meta:
        db_table = 'payment'
        ordering = ['-created_at']


class PaymentTransaction(models.Model):
    """Payment transaction log"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50)  # charge, refund, etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"

    class Meta:
        db_table = 'payment_transaction'
        ordering = ['-created_at']
