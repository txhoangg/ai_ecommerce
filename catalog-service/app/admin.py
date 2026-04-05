from django.contrib import admin
from .models import Category, Publisher, BookSeries

admin.site.register(Category)
admin.site.register(Publisher)
admin.site.register(BookSeries)
