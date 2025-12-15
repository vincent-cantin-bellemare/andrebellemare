"""
Management command to create the vcantin@codeshop.ca user.
Usage: python manage.py create_user
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import getpass


class Command(BaseCommand):
    help = 'Create the vcantin@codeshop.ca user if it does not exist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the user (if not provided, will be asked interactively)',
        )

    def handle(self, *args, **options):
        email = 'vcantin@codeshop.ca'
        username = email
        
        # Check if user already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User {email} already exists.')
            )
            return
        
        # Get password
        password = options.get('password')
        if not password:
            password = getpass.getpass('Enter password for vcantin@codeshop.ca: ')
            password_confirm = getpass.getpass('Confirm password: ')
            if password != password_confirm:
                self.stdout.write(
                    self.style.ERROR('Passwords do not match.')
                )
                return
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created user {email}')
        )

