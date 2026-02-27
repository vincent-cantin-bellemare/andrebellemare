"""
Seed command to populate the database with demo data.
Usage: python manage.py seed
"""

import os
import random
import shutil
from pathlib import Path
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings

try:
    from PIL import Image, ImageDraw
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

from apps.gallery.models import Category, Finish, Painting, PaintingImage
from apps.contact.models import FAQ, Testimonial, SiteSettings


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            PaintingImage.objects.all().delete()
            Painting.objects.all().delete()
            Category.objects.all().delete()
            Finish.objects.all().delete()
            FAQ.objects.all().delete()
            Testimonial.objects.all().delete()

        self.stdout.write('Seeding database...')

        self.create_categories()
        self.create_finishes()
        self.create_paintings()
        self.create_faqs()
        self.create_testimonials()
        self.create_site_settings()

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_categories(self):
        categories_data = [
            {'name': 'Abstraction', 'description': 'Exploration des formes et des couleurs dans un univers abstrait.', 'order': 1},
            {'name': 'Banlieue', 'description': 'Scènes de vie quotidienne dans les quartiers résidentiels.', 'order': 2},
            {'name': 'Capsules historiques', 'description': 'Évocations de notre patrimoine et de notre histoire.', 'order': 3},
            {'name': 'Éros', 'description': 'Célébration de la sensualité et de la beauté du corps.', 'order': 4},
            {'name': 'Fruits de la passion', 'description': 'Nature morte et fruits aux couleurs éclatantes.', 'order': 5},
            {'name': 'Ruelle', 'description': 'Les charmes cachés des ruelles montréalaises.', 'order': 6},
        ]

        for data in categories_data:
            Category.objects.get_or_create(name=data['name'], defaults=data)

        self.stdout.write(f'  Created {len(categories_data)} categories')

    def create_finishes(self):
        finishes_data = [
            'Époxy',
            'Encre sur toile et mortier',
            'Acrylique',
            'Huile sur toile',
            'Technique mixte',
        ]

        for name in finishes_data:
            Finish.objects.get_or_create(name=name)

        self.stdout.write(f'  Created {len(finishes_data)} finishes')

    def create_paintings(self):
        # Title components for random generation
        adjectives = [
            'Lumière', 'Éclat', 'Ombre', 'Reflet', 'Souffle', 'Murmure',
            'Danse', 'Silence', 'Rêve', 'Éveil', 'Flamme', 'Vague',
            'Brume', 'Aurore', 'Crépuscule', 'Harmonie', 'Écho', 'Passage'
        ]

        nouns = [
            'd\'automne', 'nocturne', 'printanier', 'hivernal', 'd\'été',
            'urbain', 'champêtre', 'maritime', 'céleste', 'terrestre',
            'du matin', 'du soir', 'de l\'aube', 'intérieur', 'lointain'
        ]

        descriptions = [
            "Cette œuvre capture l'essence fugace d'un moment suspendu dans le temps. Les couleurs se mêlent et se répondent dans une danse subtile.",
            "Une exploration des textures et des nuances, où chaque coup de pinceau raconte une histoire différente.",
            "L'artiste nous invite à contempler la beauté cachée dans les détails du quotidien.",
            "Une méditation visuelle sur les contrastes et les harmonies qui composent notre monde.",
            "Cette toile évoque les souvenirs et les émotions qui nous habitent, dans un langage de couleurs et de formes.",
            "Un voyage intérieur traduit en pigments et en lumière, une invitation à la contemplation.",
            "L'œuvre joue avec les perspectives et les plans pour créer une profondeur hypnotique.",
        ]

        dimensions_options = [
            '12" x 16"', '16" x 20"', '18" x 24"', '20" x 24"',
            '24" x 30"', '24" x 36"', '30" x 40"', '36" x 48"'
        ]

        categories = list(Category.objects.all())
        finishes = list(Finish.objects.all())

        # Check for images in /volumes/django/media/seed
        seed_images = []
        seed_path = Path('/volumes/django/media/seed')
        if seed_path.exists():
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']:
                seed_images.extend(seed_path.glob(ext))

        use_seed_images = len(seed_images) > 0
        if use_seed_images:
            self.stdout.write(f'  Found {len(seed_images)} images in /volumes/django/media/seed')
        else:
            self.stdout.write('  No images in /volumes/django/media/seed, generating placeholders')

        # Create paintings
        num_paintings = 18
        for i in range(num_paintings):
            title = f"{random.choice(adjectives)} {random.choice(nouns)}"
            sku = f"AB-{str(i + 1).zfill(4)}"

            # Check if painting already exists
            if Painting.objects.filter(sku=sku).exists():
                continue

            painting = Painting.objects.create(
                sku=sku,
                title=title,
                description=random.choice(descriptions),
                price_cad=Decimal(random.randrange(200, 2500, 50)),
                dimensions=random.choice(dimensions_options),
                category=random.choice(categories) if categories else None,
                finish=random.choice(finishes) if finishes else None,
                is_active=True,
                is_featured=i < 8,  # First 8 are featured
                status=random.choices(
                    ['available_maison_pere', 'available_direct', 'sold_maison_pere', 'sold_direct', 'not_for_sale'],
                    weights=[0.4, 0.3, 0.2, 0.1]
                )[0]
            )

            # Create image(s) for this painting
            num_images = random.randint(1, 3)
            for img_idx in range(num_images):
                if use_seed_images:
                    # Use image from /volumes/django/media/seed
                    src_image = random.choice(seed_images)
                    self._create_image_from_file(painting, src_image, img_idx == 0)
                elif HAS_PILLOW:
                    # Generate placeholder
                    self._create_placeholder_image(painting, img_idx == 0)

        self.stdout.write(f'  Created {num_paintings} paintings')

    def _create_image_from_file(self, painting, src_path, is_primary):
        """Copy an image file to media directory and create PaintingImage"""
        media_dir = Path(settings.MEDIA_ROOT) / 'paintings' / '2024' / '12'
        media_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{painting.sku}_{random.randint(1000, 9999)}{src_path.suffix}"
        dest_path = media_dir / filename

        shutil.copy(src_path, dest_path)

        relative_path = f"paintings/2024/12/{filename}"
        PaintingImage.objects.create(
            painting=painting,
            image=relative_path,
            alt_text=painting.title,
            is_primary=is_primary,
            order=0 if is_primary else 1
        )

    def _create_placeholder_image(self, painting, is_primary):
        """Generate a colorful abstract placeholder image"""
        media_dir = Path(settings.MEDIA_ROOT) / 'paintings' / '2024' / '12'
        media_dir.mkdir(parents=True, exist_ok=True)

        # Create abstract gradient image
        width, height = 800, 800
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)

        # Random colors for gradient
        colors = [
            (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
            for _ in range(4)
        ]

        # Create gradient effect
        for y in range(height):
            for x in range(width):
                # Blend colors based on position
                r = int((colors[0][0] * (width - x) + colors[1][0] * x) / width)
                g = int((colors[2][1] * (height - y) + colors[3][1] * y) / height)
                b = int((colors[0][2] * (width - x) + colors[2][2] * x) / width)
                draw.point((x, y), fill=(r % 256, g % 256, b % 256))

        # Add some abstract shapes
        for _ in range(random.randint(3, 8)):
            shape_color = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            )
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = x1 + random.randint(50, 300)
            y2 = y1 + random.randint(50, 300)

            if random.choice([True, False]):
                draw.ellipse([x1, y1, x2, y2], fill=shape_color, outline=None)
            else:
                draw.rectangle([x1, y1, x2, y2], fill=shape_color, outline=None)

        filename = f"{painting.sku}_{random.randint(1000, 9999)}.jpg"
        filepath = media_dir / filename
        img.save(filepath, 'JPEG', quality=85)

        relative_path = f"paintings/2024/12/{filename}"
        PaintingImage.objects.create(
            painting=painting,
            image=relative_path,
            alt_text=painting.title,
            is_primary=is_primary,
            order=0 if is_primary else 1
        )

    def create_faqs(self):
        faqs_data = [
            {
                'question': 'Comment puis-je acheter une toile?',
                'answer': '''Pour acquérir une toile, contactez la Fondation de la Maison du Père au 514-845-0168 poste 358.''',
                'order': 1,
            },
            {
                'question': 'Pourquoi le paiement se fait-il par don à la Maison du Père?',
                'answer': '''C'est ma façon de donner un sens plus profond à mon art. Chaque toile vendue permet d'aider les personnes en situation d'itinérance à Montréal.

Vous repartez avec une œuvre originale. Tout le monde y gagne!''',
                'order': 2,
            },
            {
                'question': 'Les toiles sont-elles encadrées?',
                'answer': '''Les toiles sont généralement vendues non encadrées, montées sur châssis professionnel et prêtes à accrocher. Si vous souhaitez un encadrement, je peux vous recommander des encadreurs de confiance dans la région.''',
                'order': 3,
            },
            {
                'question': 'Livrez-vous à l\'extérieur de Boucherville?',
                'answer': '''Oui! La livraison est gratuite à Boucherville et dans les municipalités avoisinantes. Pour les autres régions du Québec, des frais de livraison s'appliquent selon la destination. Contactez-moi pour obtenir un estimé.''',
                'order': 4,
                'is_active': False,
            },
            {
                'question': 'Acceptez-vous les commandes personnalisées?',
                'answer': '''Je suis ouvert aux discussions pour des projets spéciaux. Contactez-moi avec votre idée et nous pourrons en discuter ensemble. Cependant, je ne peux garantir de reproduire exactement une vision précise, car chaque œuvre reste une création artistique unique.''',
                'order': 5,
            },
        ]

        for data in faqs_data:
            FAQ.objects.get_or_create(question=data['question'], defaults=data)

        self.stdout.write(f'  Created {len(faqs_data)} FAQs')

    def create_testimonials(self):
        testimonials_data = [
            {
                'author_name': 'Marie-Claire Tremblay',
                'author_location': 'Longueuil',
                'content': 'La toile que j\'ai reçue est encore plus belle en vrai que sur les photos. André est un artiste généreux et passionné. Un vrai coup de cœur!',
                'rating': 5,
            },
            {
                'author_name': 'Jean-François Dubois',
                'author_location': 'Montréal',
                'content': 'J\'apprécie énormément le concept de don à la Maison du Père. Ça donne une dimension supplémentaire à l\'achat d\'une œuvre d\'art. Ma toile trône fièrement dans mon salon.',
                'rating': 5,
            },
            {
                'author_name': 'Sophie Bergeron',
                'author_location': 'Boucherville',
                'content': 'André m\'a livré la toile en personne. On a pu discuter de son art et de son inspiration. Une expérience humaine et chaleureuse!',
                'rating': 5,
            },
            {
                'author_name': 'Pierre Lavoie',
                'author_location': 'Saint-Bruno',
                'content': 'Troisième toile que j\'achète à André. Ses œuvres apportent de la vie et de la couleur à notre maison. Un artiste local talentueux!',
                'rating': 5,
            },
            {
                'author_name': 'Isabelle Côté',
                'author_location': 'Varennes',
                'content': 'Service impeccable et œuvre magnifique. Je recommande sans hésitation.',
                'rating': 4,
            },
        ]

        for data in testimonials_data:
            Testimonial.objects.get_or_create(
                author_name=data['author_name'],
                defaults=data
            )

        self.stdout.write(f'  Created {len(testimonials_data)} testimonials')

    def create_site_settings(self):
        SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                'meta_description': 'André Bellemare, artiste peintre à Boucherville. Découvrez ses toiles originales. Chaque achat est un don à la Maison du Père.',
                'meta_keywords': 'artiste peintre, Boucherville, toiles, art québécois, peinture, André Bellemare',
            }
        )
        self.stdout.write('  Created site settings')

