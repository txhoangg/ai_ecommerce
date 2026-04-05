from django.db import models
import uuid


class ShippingCarrier(models.Model):
    """Shipping carrier"""
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'shipping_carrier'


class Shipping(models.Model):
    """Shipping model - Shipping bounded context"""
    METHOD_CHOICES = [
        ('standard', 'Standard Shipping'),
        ('express', 'Express Shipping'),
        ('overnight', 'Overnight Shipping'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    order_id = models.IntegerField()  # Reference to order-service
    customer_id = models.IntegerField()  # Reference to customer-service
    carrier = models.ForeignKey(ShippingCarrier, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    tracking_number = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipping {self.tracking_number} - Order {self.order_id}"

    class Meta:
        db_table = 'shipping'
        ordering = ['-created_at']


class ShippingTracking(models.Model):
    """Shipping tracking log"""
    shipping = models.ForeignKey(Shipping, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shipping.tracking_number} - {self.status}"

    class Meta:
        db_table = 'shipping_tracking'
        ordering = ['-created_at']
