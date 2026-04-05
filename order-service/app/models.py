from django.db import models


class Order(models.Model):
    """Order model - Ordering bounded context"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_id = models.IntegerField()  # Reference to customer-service
    staff_id = models.IntegerField(null=True, blank=True)  # Reference to staff-service
    discount_id = models.IntegerField(null=True, blank=True)  # Reference to discount
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - Customer {self.customer_id}"

    class Meta:
        db_table = 'order'
        ordering = ['-created_at']


class OrderItem(models.Model):
    """Order items"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()  # Reference to book-service
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    
    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Order {self.order.id} - Book {self.book_id} x {self.quantity}"

    class Meta:
        db_table = 'order_item'


class Invoice(models.Model):
    """Invoice for order"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - Order {self.order.id}"

    class Meta:
        db_table = 'invoice'


class Discount(models.Model):
    """Discount code"""
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"

    class Meta:
        db_table = 'discount'


class OrderStatusHistory(models.Model):
    """Order status change history"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by_id = models.IntegerField()  # Reference to staff-service
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.order.id}: {self.old_status} → {self.new_status}"

    class Meta:
        db_table = 'order_status_history'
        ordering = ['-created_at']


class OrderReturn(models.Model):
    """Order return requests"""
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='return_request')
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='requested')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processed_by_id = models.IntegerField(null=True, blank=True)  # Reference to staff-service
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return for Order #{self.order.id} - {self.status}"

    class Meta:
        db_table = 'order_return'
