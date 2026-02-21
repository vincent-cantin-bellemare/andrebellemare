"""
Management command to seed paintings from a JSON file and images from /volumes/django/media/seeds.
Usage: python manage.py seed_from_json [--json-file=data/paintings_seed.json]
"""

import json
import shutil
import io
from pathlib import Path
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.db import transaction
from django.db.models import Max

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from apps.gallery.models import Category, Finish, Painting, PaintingImage


class Command(BaseCommand):
    help = 'Seed paintings from JSON file and images from /volumes/django/media/seeds'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            default='data/paintings_seed.json',
            help='Path to JSON file with paintings data',
        )
        parser.add_argument(
            '--seeds-dir',
            type=str,
            default=str(Path(settings.MEDIA_ROOT) / 'seeds'),
            help='Directory containing seed images',
        )

    def handle(self, *args, **options):
        json_file = Path(options['json_file'])
        seeds_dir = Path(options['seeds_dir'])

        if not json_file.exists():
            self.stdout.write(
                self.style.ERROR(f'JSON file not found: {json_file}')
            )
            return

        if not seeds_dir.exists():
            self.stdout.write(
                self.style.ERROR(f'Seeds directory not found: {seeds_dir}')
            )
            return

        # Read JSON file
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading JSON file: {str(e)}')
            )
            return

        paintings_data = data.get('paintings', [])
        if not paintings_data:
            self.stdout.write(
                self.style.WARNING('No paintings found in JSON file')
            )
            return

        self.stdout.write(f'Found {len(paintings_data)} paintings in JSON file')
        self.stdout.write(f'Scanning images in {seeds_dir}...')

        # Get list of available images
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG', '*.webp', '*.WEBP', '*.avif', '*.AVIF']
        available_images = {}
        for ext in image_extensions:
            for img_path in seeds_dir.glob(ext):
                available_images[img_path.name] = img_path
                available_images[img_path.name.lower()] = img_path

        self.stdout.write(f'Found {len(available_images)} images in seeds directory')

        created_count = 0
        error_count = 0

        with transaction.atomic():
            for painting_data in paintings_data:
                try:
                    # Get or create category
                    category_name = painting_data.get('category')
                    category = None
                    if category_name:
                        category, _ = Category.objects.get_or_create(
                            name=category_name,
                            defaults={'description': f'Catégorie {category_name}'}
                        )

                    # Get or create finish
                    finish_name = painting_data.get('finish')
                    finish = None
                    if finish_name:
                        finish, _ = Finish.objects.get_or_create(name=finish_name)

                    # Determine next painting ID (will be set when painting is created)
                    # We'll use the painting.id after creation

                    # Check if painting with this SKU already exists
                    sku = painting_data.get('sku')
                    if Painting.objects.filter(sku=sku).exists():
                        self.stdout.write(
                            self.style.WARNING(f'Skipping {sku} - already exists')
                        )
                        continue

                    # Create painting first to get its ID
                    painting = Painting.objects.create(
                        sku=sku,
                        title=painting_data.get('title', 'Sans titre'),
                        description=painting_data.get('description', ''),
                        price_cad=Decimal(str(painting_data.get('price_cad', 0))),
                        dimensions=painting_data.get('dimensions', ''),
                        category=category,
                        finish=finish,
                        status=painting_data.get('status', 'available_maison_pere'),
                        is_featured=painting_data.get('is_featured', False),
                        is_active=True,
                    )

                    # Get image filenames (support both single and multiple)
                    image_filenames = []
                    if 'image_filenames' in painting_data:
                        image_filenames = painting_data['image_filenames']
                    elif 'image_filename' in painting_data:
                        image_filenames = [painting_data['image_filename']]

                    # Process images
                    images_created = 0
                    for idx, image_filename in enumerate(image_filenames):
                        if not image_filename:
                            continue

                        # Find image file
                        image_path = available_images.get(image_filename) or available_images.get(image_filename.lower())
                        if not image_path:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Image not found for {sku}: {image_filename}'
                                )
                            )
                            continue

                        # Determine file extension and convert AVIF to JPEG if needed
                        file_ext = image_path.suffix.lower()
                        if not file_ext:
                            file_ext = '.jpg'

                        # Convert AVIF to JPEG if Pillow doesn't support AVIF or if it's AVIF format
                        image_file = None
                        if file_ext == '.avif' and HAS_PILLOW:
                            try:
                                # Try to open AVIF with Pillow
                                img = Image.open(image_path)
                                # Convert to RGB if necessary (AVIF might be RGBA)
                                if img.mode in ('RGBA', 'LA', 'P'):
                                    # Create white background for transparency
                                    background = Image.new('RGB', img.size, (255, 255, 255))
                                    if img.mode == 'P':
                                        img = img.convert('RGBA')
                                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                                    img = background
                                elif img.mode != 'RGB':
                                    img = img.convert('RGB')

                                # Save to BytesIO as JPEG
                                output = io.BytesIO()
                                img.save(output, format='JPEG', quality=95)
                                output.seek(0)
                                image_file = File(output, name=image_path.stem + '.jpg')
                                file_ext = '.jpg'
                                self.stdout.write(
                                    self.style.SUCCESS(f'Converted AVIF to JPEG for {sku}')
                                )
                            except Exception as e:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Could not convert AVIF {image_filename} for {sku}: {str(e)}. Using original file.'
                                    )
                                )
                                # Fallback to original file
                                image_file = File(open(image_path, 'rb'), name=image_path.name)
                        else:
                            # Use original file for non-AVIF formats
                            image_file = File(open(image_path, 'rb'), name=image_path.name)

                        # Create PaintingImage with the file
                        # The upload_to function will generate the path paintings/[id].ext
                        painting_image = PaintingImage(
                            painting=painting,
                            alt_text=painting.title if idx == 0 else f'{painting.title} - Vue {idx + 1}',
                            is_primary=(idx == 0),
                            order=idx,
                        )
                        # Save with converted filename if AVIF was converted, otherwise original
                        if file_ext == '.jpg' and image_path.suffix.lower() == '.avif':
                            painting_image.image.save(
                                image_path.stem + '.jpg',
                                image_file,
                                save=True
                            )
                        else:
                            painting_image.image.save(
                                image_path.name,
                                image_file,
                                save=True
                            )

                        # Close file if it was opened
                        if hasattr(image_file, 'close'):
                            image_file.close()

                        images_created += 1

                    if images_created == 0:
                        self.stdout.write(
                            self.style.WARNING(
                                f'No images created for {sku} - painting created without images'
                            )
                        )

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created {sku}: {painting.title} with {images_created} image(s)'
                        )
                    )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error creating painting {painting_data.get("sku", "unknown")}: {str(e)}'
                        )
                    )

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Successfully created {created_count} painting(s)'
            )
        )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f'✗ {error_count} error(s) occurred')
            )
