from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Staff(models.Model):
    """Staff model - Identity bounded context"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='staff')
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """Hash password before saving"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.name} ({self.role})"

    class Meta:
        db_table = 'staff'


class InventoryLog(models.Model):
    """Inventory log for tracking stock changes"""
    staff_id = models.IntegerField()  # Reference to staff who made the change
    book_id = models.IntegerField()   # Reference to book (from product-service)
    action = models.CharField(max_length=100)
    quantity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Book {self.book_id} - {self.action} - {self.quantity}"

    class Meta:
        db_table = 'inventory_log'
        ordering = ['-created_at']
