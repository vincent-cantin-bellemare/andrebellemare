"""
Management command to pre-generate all thumbnails for paintings.
Usage: python manage.py generate_thumbnails
"""
from django.core.management.base import BaseCommand
from sorl.thumbnail import get_thumbnail

from apps.gallery.models import Painting


class Command(BaseCommand):
    help = 'Pre-generate all thumbnails for paintings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sizes',
            type=str,
            default='100x100,200x200,400x400,800x800',
            help='Comma-separated list of thumbnail sizes (e.g., "100x100,200x200")',
        )

    def handle(self, *args, **options):
        sizes = [size.strip() for size in options['sizes'].split(',')]
        
        paintings = Painting.objects.filter(is_active=True).prefetch_related('images')
        total_paintings = paintings.count()
        
        self.stdout.write(f'Generating thumbnails for {total_paintings} paintings...')
        self.stdout.write(f'Sizes: {", ".join(sizes)}')
        
        generated_count = 0
        error_count = 0
        
        for painting in paintings:
            if not painting.primary_image:
                continue
            
            for size in sizes:
                try:
                    # Generate thumbnail - this will create it if it doesn't exist
                    thumb = get_thumbnail(
                        painting.primary_image.image,
                        size,
                        crop='center',
                        quality=85
                    )
                    generated_count += 1
                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error generating {size} for {painting.sku}: {str(e)}'
                        )
                    )
            
            # Also generate thumbnails for additional images
            for image in painting.images.all():
                if image == painting.primary_image:
                    continue
                
                for size in sizes:
                    try:
                        thumb = get_thumbnail(
                            image.image,
                            size,
                            crop='center',
                            quality=85
                        )
                        generated_count += 1
                    except Exception as e:
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error generating {size} for {painting.sku} image {image.id}: {str(e)}'
                            )
                        )
        
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Successfully generated {generated_count} thumbnail(s)'
            )
        )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ {error_count} error(s) occurred')
            )




