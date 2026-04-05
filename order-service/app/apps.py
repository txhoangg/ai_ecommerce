from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        import sys
        import os
        import threading
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') == 'true':
            def run_consumer():
                import time
                time.sleep(2)
                from . import consumer
                consumer.start_consuming()
            threading.Thread(target=run_consumer, daemon=True).start()
