from django.contrib import admin
from .models import (
    Book, Author, BookAuthor, BookFormat, BookImage, 
    BookTag, BookInventoryHistory
)

admin.site.register(Book)
admin.site.register(Author)
admin.site.register(BookAuthor)
admin.site.register(BookFormat)
admin.site.register(BookImage)
admin.site.register(BookTag)
admin.site.register(BookInventoryHistory)
