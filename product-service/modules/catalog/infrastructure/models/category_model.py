from django.db import models


class CategoryModel(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'catalog'
        db_table = 'categories'
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_full_path(self) -> str:
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
