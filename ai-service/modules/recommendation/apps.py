from django.apps import AppConfig


class RecommendationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.recommendation'
    label = 'recommendation'
    verbose_name = 'Recommendation Module'
