import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth import get_user_model
from cyberbullying.models import UserProfile

User = get_user_model()
try:
    if not User.objects.filter(username='admin').exists():
        user = User.objects.create_superuser('admin', 'admin@example.com', 'Admin123!')
        UserProfile.objects.get_or_create(user=user)
        print('Created admin / Admin123!')
    else:
        user = User.objects.get(username='admin')
        user.set_password('Admin123!')
        user.save()
        UserProfile.objects.get_or_create(user=user)
        print('Updated admin / Admin123!')
except Exception as e:
    print(f"Error: {e}")
