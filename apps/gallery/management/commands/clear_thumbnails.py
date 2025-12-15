"""
Management command to clear sorl-thumbnail cache.
Usage: python manage.py clear_thumbnails
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from pathlib import Path
import shutil


class Command(BaseCommand):
    help = 'Clear sorl-thumbnail cache and regenerate thumbnails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Regenerate thumbnails after clearing cache',
        )

    def handle(self, *args, **options):
        cache_dir = Path(settings.MEDIA_ROOT) / 'cache'
        
        if cache_dir.exists():
            self.stdout.write(f'Clearing cache directory: {cache_dir}')
            try:
                shutil.rmtree(cache_dir)
                cache_dir.mkdir(parents=True, exist_ok=True)
                self.stdout.write(self.style.SUCCESS('Cache cleared successfully!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error clearing cache: {e}'))
        else:
            self.stdout.write('Cache directory does not exist, creating it...')
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.SUCCESS('Cache directory created!'))
        
        # Clear sorl-thumbnail database cache
        try:
            self.stdout.write('Clearing sorl-thumbnail database cache...')
            call_command('thumbnail', 'clear')
            self.stdout.write(self.style.SUCCESS('Database cache cleared!'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not clear database cache: {e}'))
        
        if options['regenerate']:
            self.stdout.write('Regenerating thumbnails...')
            try:
                call_command('thumbnail', 'cleanup')
                self.stdout.write(self.style.SUCCESS('Thumbnails regenerated!'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Could not regenerate thumbnails: {e}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Cache clearing completed!'))
        self.stdout.write('💡 Thumbnails will be regenerated automatically on next page load.')






