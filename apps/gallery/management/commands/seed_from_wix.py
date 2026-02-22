"""
Management command to import paintings from the old Wix website.
Downloads images from Wix CDN and creates paintings in the database.

Usage: python manage.py seed_from_wix [--dry-run] [--force] [--skip-images]
"""

import re
import io
import ssl
import traceback
import urllib.request
import urllib.error
from html.parser import HTMLParser
from pathlib import Path
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.db import transaction

from apps.gallery.models import Category, Finish, Painting, PaintingImage


# Raw CSV data from Wix export (only Product rows, not Variants)
WIX_CSV_DATA = """handleId	fieldType	name	description	productImageUrl	collection	sku	ribbon	price	surcharge	visible	discountMode	discountValue	inventory
product_95c4d933-9550-04c4-bb7a-e60348388773	Product	Nature en feu	<p>encre sur toile galerie et mortier</p><p>fini époxy</p><p>30x30</p>	05fe93_e529ae24e9a14aa58381dd258369857d~mv2.jpg	Fruits de la passion	Fr-53		0.0		TRUE	PERCENT	0.0	OutOfStock
product_be8f6af3-6b86-d1a3-9ec8-a3beaa7fd110	Product	Nature...fruits et talon	<p>encre sur toile et mortier</p><p>fini époxy</p><p>8x10</p><p>&nbsp;</p>	05fe93_9c58297fd1ec4bb3a89bdabd02bd2aa3~mv2.jpg	Fruits de la passion	Fr-52		0.0		TRUE	PERCENT	0.0	OutOfStock
product_be286d63-9efa-1dce-c621-22537261dad7	Product	Nature...vignes sensuelles	<p>Encre sur toile et mortier</p><p>fini époxy</p><p>12x10</p>	05fe93_020828b62f774ed09453be7dcd848faf~mv2.jpg	Fruits de la passion	Fr-51		0.0		TRUE	PERCENT	0.0	OutOfStock
product_e1430440-ea17-ca10-cf7c-f7d2af7147b0	Product	Nature ...vignes	<p>encre sur toile et mortier</p><p>fini époxy 24x24</p>	05fe93_1a8dcade4445476aa9417a8d71c6cc14~mv2.jpg	Fruits de la passion	Fr-44		0.0		TRUE	PERCENT	0.0	InStock
product_79df9df3-e8ef-543a-75df-f70955d7b2cf	Product	Nature ...fleurs	<p>Acrylique sur toile</p><p>18x24</p>	05fe93_f82ba28d35b14000a188e7b9c9a638c9~mv2.jpg	Fruits de la passion	Fr-43		0.0		TRUE	PERCENT	0.0	OutOfStock
product_e4d60e95-c573-0590-741c-3071625dcffa	Product	Nature...vignes et fruits	<p>encre&nbsp;sur toile et mortier</p><p>fini époxy&nbsp; 20x16</p>	05fe93_3add9f4c640a4f759c9d20139755e344~mv2.jpg	Fruits de la passion	Fr-41		0.0		TRUE	PERCENT	0.0	OutOfStock
product_3d59ca37-6949-deec-e9b0-b7e59e4ada75	Product	Nature...raisins et bananes	<p>encre sur toile et mortier</p><p>fini époxy&nbsp;</p><p>10x20</p>	05fe93_49775a2e475f49ee8198d21cb87f70a5~mv2.jpg	Fruits de la passion	Fr-40		0.0		TRUE	PERCENT	0.0	OutOfStock
product_2abc3c21-1cdc-1920-3c0e-c507fbea8c43	Product	Gerbe en or	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>12x16</p>	05fe93_274d3315b2b14d4c98c602e1f130cae3~mv2.jpg	Fruits de la passion	Fr-10		0.0		TRUE	PERCENT	0.0	OutOfStock
product_be21fd6d-29c4-b581-fcce-dfb1a910978d	Product	Panier de fruits et légumes	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>40x30 pces</p><p>&nbsp;</p>	05fe93_3badebece43e4b9ea27421037f9bf6a8~mv2.jpg	Fruits de la passion	Fr-25		0.0		TRUE	PERCENT	0.0	OutOfStock
product_b842f3de-4f07-af92-0d1b-0878fb758531	Product	Triptyque	<p>Encre sur toile galerie et mortier</p><p>Fini époxy</p><p>10x48 pces&nbsp; 2x</p><p>24x48 pces</p><p>&nbsp;</p>	05fe93_7a6bc7233bc0483ea9136f0963059a8c~mv2.jpg	Fruits de la passion	Fr-58		0.0		TRUE	PERCENT	0.0	OutOfStock
product_8d58a293-34ee-6e23-92e9-e5ce399b2064	Product	Raisins	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>12x18 pces</p>	05fe93_919056ecbdb34108913961140709dbcd~mv2.jpg	Fruits de la passion	Fr-12		0.0		TRUE	PERCENT	0.0	OutOfStock
product_cfe249dd-17bb-6cdc-5a6f-4bcee11ccba1	Product	Trois bananes	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>16x12 pces</p>	05fe93_6070b02486bc4a83a1d10338832de97a~mv2.jpg	Fruits de la passion	Fr-14		0.0		TRUE	PERCENT	0.0	OutOfStock
product_479372d5-7264-3753-abe7-c22d319ec4f5	Product	Nature...quatre fruits	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>16x16 pces</p>	05fe93_0ec46fd5c37a471c95d4ffb95456d9df~mv2.jpg	Fruits de la passion	FR-16		0.0		TRUE	PERCENT	0.0	OutOfStock
product_8f12aab8-6463-7be5-c5f8-3bb9293a1192	Product	Nature ... un ananas	<p>Encre sur toile et mortier</p><p>20x18 pces&nbsp;</p><p>Fini époxy</p><p>Toile galerie</p>	05fe93_51bc5fbb85f346f5a04cba0914a30d7d~mv2.jpg	Fruits de la passion	FR-17		0.0		TRUE	PERCENT	0.0	OutOfStock
product_cb87dfb9-4822-6288-09ae-25552a654a4e	Product	Nature...avec insecte	<p>Encre sur toile mortier</p><p>Fini&nbsp; époxy</p><p>24x24&nbsp;</p><p>Toile galerie</p><p>&nbsp;</p>	05fe93_68c414712a5249b7a1ca1d8fca79c79d~mv2.jpg	Fruits de la passion	Fr-18		0.0		TRUE	PERCENT	0.0	OutOfStock
product_7709ed7a-97d0-bfca-88d1-7e710ed32d8b	Product	Gerbe bleutée	<p>Encre sur toile et motier</p><p>Fini époxy</p><p>20x24</p>	05fe93_882de96210764226bdcc450560a54a96~mv2.jpg	Fruits de la passion	FR-20		0.0		TRUE	PERCENT	0.0	OutOfStock
product_af15b5a0-fd0e-3e85-65c3-709463383266	Product	Gerbe en or	<p>Encre sur toile et mortier</p><p>30x48 pces</p><p>Fini époxy</p>	05fe93_e5741fc88f9746efbc97183f1dcaad03~mv2.jpg	Fruits de la passion	Fr-23		0.0		TRUE	PERCENT	0.0	OutOfStock
product_3e4488ac-36b7-cfaa-df78-96ba9f1aeeea	Product	Deux ananas...	<p>Encre sur oile et mortier</p><p>Fini époxy</p><p>48x48 pces</p>	05fe93_ffaccc8b4cce46d69571aca4379367ac~mv2.jpg	Fruits de la passion	FR-26		0.0		TRUE	PERCENT	0.0	OutOfStock
product_749db531-ebaa-d00e-3430-9f1ed12870dc	Product	Gros panier de fruits	<p>Encre sur toile galerie et mortier</p><p>Triptyque 10x48 pces&nbsp; 2x&nbsp;</p><p>24x48 pces</p><p>Fini époxy</p>	05fe93_d26cb0c56b5246cc9e8fee897b6bec1b~mv2.jpg	Fruits de la passion	Fr-27		0.0		TRUE	PERCENT	0.0	OutOfStock
product_42b53da6-715f-57a0-c7a6-cea6951a5e7e	Product	Nature...cuivre	<p>Huile sur toile</p><p>Encadrement</p><p>12x18</p>	05fe93_e40d58f91dbe4c369fe5d27bf6f90967~mv2.jpg	Fruits de la passion	FR-28		0.0		TRUE	PERCENT	0.0	InStock
product_7be454d8-1206-1035-4f81-46d523b75211	Product	Nature...osier	<p>Huile sur toile</p><p>Encadrement</p><p>14x12 pces</p>	05fe93_6e9fe07960a74fcc8ecde617bce3750f~mv2.jpg	Fruits de la passion	Fr29		0.0		TRUE	PERCENT	0.0	InStock
product_57de5e89-1d58-331d-a311-36df9bf54c71	Product	Nature ...théière	<p>Huile sur toile</p><p>Encadrement</p><p>18x12 pces</p>	05fe93_828ebeba1ae143f1bd7b5e5b59dadbea~mv2.jpg	Fruits de la passion	Fr-31		0.0		TRUE	PERCENT	0.0	OutOfStock
product_1ff4a66c-2367-23aa-3512-6a83b5576387	Product	Nature ...vin	<p>Acrylique sur toile</p><p>14x18 pces</p>	05fe93_c742d4b44507443a95022b27479dc051~mv2.jpg	Fruits de la passion	Fr-30		0.0		TRUE	PERCENT	0.0	OutOfStock
product_a3a51160-f193-430c-1c4a-315ced261bee	Product	Trois bananes	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>18x14 pces</p>	05fe93_74daf623a2fe41149ce46b6df1da25ff~mv2.jpg	Fruits de la passion	FR-32		0.0		TRUE	PERCENT	0.0	InStock
product_dc07df96-f126-6751-ad4e-bd6b66980e84	Product	Panier de fruits	<p>Encre sur mortier</p><p>Toile galerie</p><p>Fini époxy</p><p>36x36 pces</p>	05fe93_7cead64deaaa4c568456431d094830de~mv2.jpg	Fruits de la passion	FR-24		0.0		TRUE	PERCENT	0.0	OutOfStock
product_2fa22a68-b89d-7151-efe7-623ebfb4500a	Product	Gerbe...raisins bleus	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>12x6 pces</p><p>&nbsp;</p><p>&nbsp;</p>	05fe93_0c998126139a4f618ba29cefb7c4c181~mv2.jpg	Fruits de la passion	Fr-35		0.0		TRUE	PERCENT	0.0	OutOfStock
product_d6b0090a-5550-91ca-082d-29403e165e18	Product	Nature ...chandelle	<p>Huile sur panneau bois</p><p>20x18 pces</p><p>fini époxy</p>	05fe93_96bce44c97cb4ce9b47efd9a39ab430e~mv2.jpg	Fruits de la passion	Fr-34		0.0		TRUE	PERCENT	0.0	OutOfStock
product_ac03f476-51e0-1904-598f-1a038c36842d	Product	Nature et chaise	<p>Acrylique sur toile</p><p>12x14 pces</p>	05fe93_3eaf4fb5e4084bedb3e3453d97b7d1d2~mv2.jpg	Fruits de la passion	Fr-36		0.0		TRUE	PERCENT	0.0	OutOfStock
product_10f0688f-25ce-6a5a-c1e7-0f965dcf808b	Product	Bananes et fleurs	<p>Encre sur toile et mortier</p><p>Fini époxy</p><p>14x11 pces</p>	05fe93_11769c8424fa4e28a7a669800c86babf~mv2.jpg	Fruits de la passion	Fr-37		0.0		TRUE	PERCENT	0.0	OutOfStock
product_16c15c36-4787-4870-1ee8-8d7c802c64a7	Product	Nature érotique	<p>Encre sur toile et mortier</p><p>Fini epoxy</p><p>24x24 pces</p>	05fe93_b872c4fea695436687088d3d6c33ce2d~mv2.jpg	Abstraction	Fr-38		0.0		TRUE	PERCENT	0.0	OutOfStock
product_067f1924-e7c8-6fc8-824f-4a4ab48066f1	Product	Gerbe A	<p>Encre sur mortier</p><p>Fini époxy</p><p>30x30 pces</p>	05fe93_22070c33c0c84ef8a8194d0186251893~mv2.jpg	Fruits de la passion	Fr-39		0.0		TRUE	PERCENT	0.0	OutOfStock
product_56dfcc73-42ec-88e6-4ebd-0cea80833169	Product	Gerbe et talon haut	<p>Acrylique sur toile</p><p>12x24 pces</p><p>Fini époxy</p>	05fe93_8f9e60007adf430989bf2fda71432361~mv2.jpg	Fruits de la passion	Fr-11		0.0		TRUE	PERCENT	0.0	OutOfStock
product_8907779d-99e2-8112-3a54-63493113686a	Product	Nature morte-cuivre	<p>Acrylique sur toile 14x18 pces</p><p>Fini époxy</p>	05fe93_ed6bf874653b48028ebc63905ca2cc20~mv2.jpg	Fruits de la passion	Fr-5		0.0		TRUE	PERCENT	0.0	OutOfStock
product_8097b98c-2e2e-e7b2-7b95-360b369e15e0	Product	Horse boat Lévis-Québec		05fe93_c5b4bd639be1422bb527321603ee0f8e~mv2.jpg	Capsules historiques	Ca-2		0.0		TRUE	PERCENT	0.0	InStock
product_9df2ffb7-02dd-599a-0533-55fbc1bb7659	Product	Vielle forge de Boucherville	<p>Encre de chine sur toile</p>	05fe93_87705c40774b447188942bfaf60dae96~mv2.jpg	Capsules historiques	Ca-1		0.0		TRUE	PERCENT	0.0	InStock
product_7faec9e1-f241-12f3-b3ed-14e885c35e1e	Product	Guerre des moppes base	<p>Giclée sur toile</p><p>Finition gel acrylique</p>	05fe93_e935c907d9f44303a407be7029ec4b86~mv2.jpg	Ruelles	RU-22		250.0		TRUE	PERCENT	0.0	InStock
product_7440bfb3-8d7c-16bc-4b39-5f117b321546	Product	Neigeux	<p>Giclée sur toile 36x12 pces</p><p>Finition gel acrylique</p>	05fe93_633ab2fb0119432e9a38f510d2491ff0~mv2.jpg		RU-21		200.0		TRUE	PERCENT	0.0	InStock
product_6b58d7fd-ffd6-bd91-d64d-2c6b00360393	Product	Poly	<p>Giclée sur toile 48x 36 pces</p><p>Finition gel acrylique</p>	05fe93_65261c35ae694dd6a571013fdedd62a8~mv2.jpg	Banlieue	RU-20		350.0		TRUE	PERCENT	0.0	InStock
product_56c7f7d9-d648-1ff7-dcdf-8062ae1e0462	Product	Guerre des moppes	<p>Giclée sur toile 20x20&nbsp;pces</p><p>Finition gel acrylique</p>	05fe93_e935c907d9f44303a407be7029ec4b86~mv2.jpg	Ruelles	RU-19		350.0		TRUE	PERCENT	0.0	InStock"""

# Wix CDN base URL for images
WIX_IMAGE_BASE_URL = "https://static.wixstatic.com/media/"


class HTMLTextExtractor(HTMLParser):
    """Simple HTML parser to extract text content from HTML."""

    def __init__(self):
        super().__init__()
        self.paragraphs = []
        self.current_text = ""

    def handle_data(self, data):
        self.current_text += data

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.current_text = ""

    def handle_endtag(self, tag):
        if tag == 'p':
            text = self.current_text.strip()
            # Clean up &nbsp; and extra whitespace
            text = text.replace('\xa0', ' ').strip()
            if text:
                self.paragraphs.append(text)
            self.current_text = ""


def parse_html_description(html_desc):
    """
    Parse HTML description to extract medium, finish, and dimensions.
    Returns: (medium, finish_name, dimensions, clean_description)
    """
    if not html_desc:
        return None, None, None, ""

    # Parse HTML to get paragraphs
    parser = HTMLTextExtractor()
    try:
        parser.feed(html_desc)
    except Exception:
        return None, None, None, html_desc

    paragraphs = parser.paragraphs
    if not paragraphs:
        return None, None, None, ""

    medium = None
    finish_name = None
    dimensions = None
    other_info = []

    # Dimension pattern: look for NxN or NxN pces format
    dimension_pattern = re.compile(r'(\d+\s*x\s*\d+(?:\s*pces?)?)', re.IGNORECASE)

    # Finish patterns
    finish_patterns = [
        r'fini\s*époxy',
        r'fini\s*epoxy',
        r'finition\s+gel\s+acrylique',
        r'encadrement',
    ]

    # Medium patterns - these typically describe the technique/support
    medium_keywords = [
        'encre', 'acrylique', 'huile', 'giclée',
        'sur toile', 'sur panneau', 'sur mortier'
    ]

    for para in paragraphs:
        para_lower = para.lower()

        # Check for finish
        is_finish = False
        for fp in finish_patterns:
            if re.search(fp, para_lower):
                finish_name = para
                is_finish = True
                # Also check if dimensions are embedded in finish line
                dim_match = dimension_pattern.search(para)
                if dim_match and not dimensions:
                    dimensions = dim_match.group(1).strip()
                break

        if is_finish:
            continue

        # Check for pure dimension line
        dim_match = dimension_pattern.search(para)
        if dim_match:
            # Check if this line is primarily a dimension
            dim_text = dim_match.group(1)
            remaining = para.replace(dim_text, '').strip()
            if len(remaining) < 5:  # Pure dimension line
                dimensions = dim_text.strip()
                continue

        # Check for medium (technique)
        is_medium = False
        for mk in medium_keywords:
            if mk in para_lower:
                # This is likely a medium/technique description
                if not medium:
                    medium = para
                    # Check if dimensions are embedded
                    dim_match = dimension_pattern.search(para)
                    if dim_match and not dimensions:
                        dimensions = dim_match.group(1).strip()
                is_medium = True
                break

        if is_medium:
            continue

        # Check if it's a dimension-only line we missed
        if dimension_pattern.match(para.strip()):
            if not dimensions:
                dimensions = para.strip()
            continue

        # Add to other info if meaningful
        if para.strip() and para.strip().lower() != 'toile galerie':
            other_info.append(para)

    # Build clean description
    clean_description = "\n".join(other_info) if other_info else ""

    return medium, finish_name, dimensions, clean_description


def download_image(image_filename, timeout=60):
    """
    Download an image from Wix CDN.
    Returns: (bytes content, error_message) - content is None if failed.
    """
    url = WIX_IMAGE_BASE_URL + image_filename
    errors = []

    # Try with requests library first (more reliable)
    try:
        import requests
        response = requests.get(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            },
            timeout=timeout,
            verify=True
        )
        if response.status_code == 200:
            return response.content, None
        else:
            errors.append(f"requests: HTTP {response.status_code}")
    except ImportError:
        errors.append("requests: not installed")
    except Exception as e:
        errors.append(f"requests: {type(e).__name__}: {str(e)}")

    # Fallback to urllib with SSL context
    try:
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        # Create SSL context
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            return response.read(), None
    except urllib.error.HTTPError as e:
        errors.append(f"urllib: HTTP {e.code} {e.reason}")
    except urllib.error.URLError as e:
        errors.append(f"urllib: URLError {str(e.reason)}")
    except ssl.SSLError as e:
        errors.append(f"urllib: SSLError {str(e)}")
    except Exception as e:
        errors.append(f"urllib: {type(e).__name__}: {str(e)}")

    # Return all errors for debugging
    return None, " | ".join(errors)


class Command(BaseCommand):
    help = 'Import paintings from the old Wix website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse data and show what would be imported without making changes',
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Skip downloading images (useful for testing)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Delete and recreate paintings that already exist',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        skip_images = options['skip_images']
        force = options['force']

        self.stdout.write('Parsing Wix CSV data...')

        # Parse the CSV data
        lines = WIX_CSV_DATA.strip().split('\n')
        header = lines[0].split('\t')
        products = []

        for line in lines[1:]:
            fields = line.split('\t')
            if len(fields) < len(header):
                fields.extend([''] * (len(header) - len(fields)))

            row = dict(zip(header, fields))

            # Only process Product rows (not Variant)
            if row.get('fieldType') != 'Product':
                continue

            # Skip rows without image
            if not row.get('productImageUrl'):
                self.stdout.write(
                    self.style.WARNING(f"Skipping {row.get('name', 'unknown')} - no image")
                )
                continue

            products.append(row)

        self.stdout.write(f'Found {len(products)} products to import')

        if dry_run:
            self.stdout.write(self.style.WARNING('\n=== DRY RUN MODE ===\n'))

        # Get or create the "Nature morte" category
        category_name = "Nature morte"
        if not dry_run:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'description': 'Natures mortes importées du site Wix',
                    'order': 10
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category_name}')
                )
        else:
            self.stdout.write(f'Would create/use category: {category_name}')

        created_count = 0
        skipped_count = 0
        error_count = 0

        # Prepare media directory
        paintings_dir = Path(settings.MEDIA_ROOT) / 'paintings'
        if not dry_run:
            paintings_dir.mkdir(parents=True, exist_ok=True)

        for product in products:
            sku = product.get('sku', '').lower().strip()
            if not sku:
                self.stdout.write(
                    self.style.WARNING(f"Skipping {product.get('name')} - no SKU")
                )
                continue

            title = product.get('name', 'Sans titre').strip()
            description_html = product.get('description', '')
            image_filename = product.get('productImageUrl', '').strip()
            inventory = product.get('inventory', 'OutOfStock')
            price = product.get('price', '0.0')

            try:
                price_decimal = Decimal(str(price).replace(',', '.'))
            except Exception:
                price_decimal = Decimal('0.00')

            # Parse description for medium, finish, dimensions
            medium, finish_name, dimensions, clean_desc = parse_html_description(
                description_html
            )

            # Determine status based on inventory
            if inventory == 'InStock':
                status = 'available_maison_pere'
            else:
                status = 'sold_maison_pere'

            # Format dimensions if found
            if dimensions:
                # Clean up dimensions format
                dimensions = dimensions.replace('pces', '').strip()
                dimensions = re.sub(r'\s+', '', dimensions)  # Remove spaces
                # Add unit if not present
                if 'x' in dimensions.lower():
                    dimensions = dimensions.replace('x', '" x ') + '"'
                    dimensions = dimensions.replace('""', '"')  # Fix double quotes

            if dry_run:
                self.stdout.write(f'\n--- {sku} ---')
                self.stdout.write(f'  Title: {title}')
                self.stdout.write(f'  Medium: {medium}')
                self.stdout.write(f'  Finish: {finish_name}')
                self.stdout.write(f'  Dimensions: {dimensions}')
                self.stdout.write(f'  Status: {status}')
                self.stdout.write(f'  Price: {price_decimal}')
                self.stdout.write(f'  Image: {image_filename}')
                continue

            # Check if painting already exists
            existing = Painting.objects.filter(sku=sku).first()
            if existing:
                if force:
                    self.stdout.write(
                        self.style.WARNING(f'Deleting existing {sku} (--force)')
                    )
                    existing.delete()
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping {sku} - already exists (use --force to override)')
                    )
                    skipped_count += 1
                    continue

            try:
                with transaction.atomic():
                    # Get or create finish
                    finish = None
                    if finish_name:
                        # Normalize finish name
                        normalized_finish = finish_name.strip()
                        if re.search(r'époxy|epoxy', normalized_finish, re.IGNORECASE):
                            normalized_finish = 'Époxy'
                        elif 'gel acrylique' in normalized_finish.lower():
                            normalized_finish = 'Gel acrylique'
                        elif 'encadrement' in normalized_finish.lower():
                            normalized_finish = 'Encadrement'

                        finish, _ = Finish.objects.get_or_create(name=normalized_finish)

                    # Create painting
                    painting = Painting.objects.create(
                        sku=sku,
                        title=title,
                        description='',
                        price_cad=price_decimal,
                        dimensions=dimensions or '',
                        category=category,
                        finish=finish,
                        status=status,
                        is_active=True,
                        is_featured=False,
                    )

                    # Download and attach image
                    image_created = False
                    if not skip_images and image_filename:
                        # Always download the image (each painting gets its own copy)
                        self.stdout.write(f'  Downloading {image_filename}...')
                        image_data, error_msg = download_image(image_filename)

                        if image_data:
                            # Save image
                            image_file = io.BytesIO(image_data)
                            # Determine extension from filename
                            ext = image_filename.split('.')[-1] if '.' in image_filename else 'jpg'

                            painting_image = PaintingImage(
                                painting=painting,
                                alt_text=title,
                                is_primary=True,
                                order=0,
                            )
                            painting_image.image.save(
                                f'{sku}.{ext}',
                                File(image_file, name=f'{sku}.{ext}'),
                                save=True
                            )
                            image_created = True
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  Failed to download image for {sku}: {error_msg}'
                                )
                            )

                    created_count += 1
                    img_status = 'with image' if image_created else 'without image'
                    self.stdout.write(
                        self.style.SUCCESS(f'Created {sku}: {title} ({img_status})')
                    )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'Error creating {sku}: {str(e)}')
                )

        # Summary
        self.stdout.write('')
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would import {len(products)} paintings')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} painting(s)')
            )
            if skipped_count > 0:
                self.stdout.write(f'Skipped {skipped_count} (already exist)')
            if error_count > 0:
                self.stdout.write(
                    self.style.ERROR(f'{error_count} error(s) occurred')
                )
