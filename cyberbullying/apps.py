# Create apps.py in your cyberbullying app if it doesn't exist
# cyberbullying/apps.py
from django.apps import AppConfig

class CyberbullyingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cyberbullying'

    def ready(self):
        # Import here to avoid circular imports
        from .ml_views import ready_model
        ready_model()