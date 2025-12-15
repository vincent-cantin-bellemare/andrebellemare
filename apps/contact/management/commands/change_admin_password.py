"""
Management command to change admin superuser password.
Usage: python manage.py change_admin_password
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Change the password of the admin superuser to "admin"'

    def handle(self, *args, **options):
        username = 'admin'
        
        try:
            user = User.objects.get(username=username)
            if not user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(f'User {username} exists but is not a superuser.')
                )
                return
            
            # Set password to "admin"
            user.set_password('admin')
            user.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully changed password for superuser {username} to "admin"')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Superuser {username} does not exist. Please create it first with: python manage.py createsuperuser')
            )
