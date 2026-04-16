from django.db import models


class BookTypeModel(models.Model):
    type_key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    name_vi = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    attribute_schema = models.JSONField(default=dict)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'book_types'
        ordering = ['name']

    def __str__(self):
        return f"{self.name_vi} ({self.type_key})"
