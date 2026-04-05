from django.contrib import admin
from .models import Order, OrderItem, Invoice, Discount, OrderStatusHistory, OrderReturn

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Invoice)
admin.site.register(Discount)
admin.site.register(OrderStatusHistory)
admin.site.register(OrderReturn)
