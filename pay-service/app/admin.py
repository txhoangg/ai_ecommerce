from django.contrib import admin
from .models import Payment, PaymentTransaction

admin.site.register(Payment)
admin.site.register(PaymentTransaction)
