"""
Management command to test email configuration.
Usage: python manage.py test_email
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Send a test email to verify SMTP configuration'

    def handle(self, *args, **options):
        recipients = ['cantinbellemare@gmail.com', 'andrebellemare@live.com']
        
        self.stdout.write('Testing email configuration...')
        self.stdout.write(f'From: {settings.DEFAULT_FROM_EMAIL}')
        self.stdout.write(f'To: {", ".join(recipients)}')
        self.stdout.write(f'SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
        self.stdout.write('')
        
        try:
            send_mail(
                subject='[Test] Email de test - André Bellemare',
                message='Ceci est un email de test pour vérifier la configuration SMTP du site andrebellemare.com.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            self.stdout.write(
                self.style.SUCCESS('✓ Email sent successfully!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Failed to send email: {str(e)}')
            )







