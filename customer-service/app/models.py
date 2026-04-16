from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Customer(models.Model):
    """Customer model - Identity bounded context"""
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        """Hash password before saving"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'customer'


class Address(models.Model):
    """Customer address"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    num = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.num} {self.street}, {self.city}"

    class Meta:
        db_table = 'address'


class Membership(models.Model):
    """Customer membership level"""
    LEVEL_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='membership')
    level = models.CharField(max_length=255, choices=LEVEL_CHOICES, default='bronze')
    point = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.customer.name} - {self.level} ({self.point} points)"

    class Meta:
        db_table = 'membership'


class Notification(models.Model):
    """Customer notifications"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.title}"

    class Meta:
        db_table = 'notification'
        ordering = ['-created_at']


class Wishlist(models.Model):
    """Customer wishlist"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wishlist of {self.customer.name}"

    class Meta:
        db_table = 'wishlist'


class WishlistItem(models.Model):
    """Items in wishlist"""
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()  # Reference to product-service
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Book {self.book_id} in wishlist {self.wishlist.id}"

    class Meta:
        db_table = 'wishlist_item'
        unique_together = ('wishlist', 'book_id')


class CustomerPreference(models.Model):
    """Customer preferences"""
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='preference')
    favorite_category = models.CharField(max_length=255, blank=True)
    favorite_author = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=50, default='en')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)

    def __str__(self):
        return f"Preferences of {self.customer.name}"

    class Meta:
        db_table = 'customer_preference'


class LoginHistory(models.Model):
    """Login history tracking"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='login_history')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=50)
    device = models.CharField(max_length=255)
    success = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.customer.name} - {self.login_time}"

    class Meta:
        db_table = 'login_history'
        ordering = ['-login_time']


class CustomerSupport(models.Model):
    """Customer support tickets"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer.name} - {self.subject}"

    class Meta:
        db_table = 'customer_support'
        ordering = ['-created_at']


class CustomerReview(models.Model):
    """Customer service review"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='service_reviews')
    rating = models.IntegerField()  # 1-5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.rating} stars"

    class Meta:
        db_table = 'customer_review'
        ordering = ['-created_at']
