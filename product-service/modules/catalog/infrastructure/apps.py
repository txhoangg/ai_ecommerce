from django.apps import AppConfig


class CatalogInfrastructureConfig(AppConfig):
    name = 'modules.catalog.infrastructure'
    label = 'catalog'
    verbose_name = 'Catalog Infrastructure'

    def ready(self):
        pass
