# Create apps.py in your cyberbullying app if it doesn't exist
# cyberbullying/apps.py
from django.apps import AppConfig

class CyberbullyingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cyberbullying'
