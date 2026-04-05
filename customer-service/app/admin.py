from django.contrib import admin
from .models import (
    Customer, Address, Membership, Notification, Wishlist, WishlistItem,
    CustomerPreference, LoginHistory, CustomerSupport, CustomerReview
)

admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Membership)
admin.site.register(Notification)
admin.site.register(Wishlist)
admin.site.register(WishlistItem)
admin.site.register(CustomerPreference)
admin.site.register(LoginHistory)
admin.site.register(CustomerSupport)
admin.site.register(CustomerReview)
