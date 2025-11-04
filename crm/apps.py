# crm/apps.py
from django.apps import AppConfig
import os


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'

    def ready(self):
        # Only start the scheduler when running the development server or in a worker
        if os.environ.get('RUN_MAIN') or 'runserver' in os.sys.argv:
            # Avoid running twice in development (due to auto-reload)
            from .scheduler import start_scheduler
            start_scheduler()