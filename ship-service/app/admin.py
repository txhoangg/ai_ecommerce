from django.contrib import admin
from .models import Shipping, ShippingCarrier, ShippingTracking

admin.site.register(Shipping)
admin.site.register(ShippingCarrier)
admin.site.register(ShippingTracking)
