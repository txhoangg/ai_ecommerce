from django.db import models


class Cart(models.Model):
    """Shopping cart - Ordering bounded context"""
    customer_id = models.IntegerField()  # Reference to customer-service
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Cart {self.id} - Customer {self.customer_id}"

    def get_total(self):
        """Calculate total price of all items in cart"""
        total = sum(item.subtotal for item in self.items.all())
        return total

    class Meta:
        db_table = 'cart'


class CartItem(models.Model):
    """Items in shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()  # Reference to book-service
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Cached price at time of adding
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.price * self.quantity

    def __str__(self):
        return f"Book {self.book_id} x {self.quantity}"

    class Meta:
        db_table = 'cart_item'
        unique_together = ('cart', 'book_id')  # One book per cart
