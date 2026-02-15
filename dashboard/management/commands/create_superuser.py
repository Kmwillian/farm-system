import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
       help = 'Create superuser if none exists'

       def handle(self, *args, **options):
           User = get_user_model()
           
           username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
           password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'farm2024')
           
           if not User.objects.filter(username=username).exists():
               User.objects.create_superuser(
                   username=username,
                   email='admin@farm.com',
                   password=password
               )
               self.stdout.write(self.style.SUCCESS('Superuser created!'))