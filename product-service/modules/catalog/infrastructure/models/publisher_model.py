from django.db import models


class PublisherModel(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'publishers'
        ordering = ['name']

    def __str__(self):
        return self.name
