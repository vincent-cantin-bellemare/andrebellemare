from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def painting_image_upload_to(instance, filename):
    """
    Generate upload path for painting images using format: paintings/[painting_id].ext
    """
    # Get file extension
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    # Use painting ID if available, otherwise use a placeholder
    if instance.painting_id:
        return f'paintings/{instance.painting_id}.{ext}'
    # Fallback to date-based path if painting not yet saved
    from django.utils import timezone
    return f'paintings/{timezone.now().year}/{timezone.now().month}/{filename}'


class Category(models.Model):
    """Category for paintings (e.g., Abstraction, Banlieue, etc.)"""
    
    name = models.CharField('Nom', max_length=100)
    slug = models.SlugField('Slug', max_length=100, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    order = models.PositiveIntegerField('Ordre', default=0)
    
    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('gallery:category', kwargs={'slug': self.slug})
    
    @property
    def painting_count(self):
        return self.paintings.filter(is_active=True).count()


class Finish(models.Model):
    """Finish type for paintings (e.g., Époxy, Encre sur toile et mortier)"""
    
    name = models.CharField('Nom', max_length=100)
    
    class Meta:
        verbose_name = 'Finition'
        verbose_name_plural = 'Finitions'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Painting(models.Model):
    """A painting/artwork by André Bellemare"""
    
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('sold', 'Vendu'),
        ('not_for_sale', 'Non à vendre'),
    ]
    
    # Basic info
    sku = models.CharField('SKU', max_length=20, unique=True)
    title = models.CharField('Titre', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    
    # Pricing and dimensions
    price_cad = models.DecimalField('Prix (CAD)', max_digits=10, decimal_places=2)
    dimensions = models.CharField('Dimensions', max_length=100, help_text='Ex: 24" x 36" ou 60cm x 90cm')
    
    # Categorization
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='paintings',
        verbose_name='Catégorie'
    )
    finish = models.ForeignKey(
        Finish, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='paintings',
        verbose_name='Finition'
    )
    
    # Status
    is_active = models.BooleanField('Actif', default=True, help_text='Visible sur le site')
    is_featured = models.BooleanField('Vedette', default=False, help_text='Afficher sur la page d\'accueil')
    status = models.CharField('Statut', max_length=20, choices=STATUS_CHOICES, default='available')
    
    # Metadata
    created_at = models.DateTimeField('Créé le', auto_now_add=True)
    updated_at = models.DateTimeField('Modifié le', auto_now=True)
    
    class Meta:
        verbose_name = 'Toile'
        verbose_name_plural = 'Toiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sku} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure unique slug
            counter = 1
            original_slug = self.slug
            while Painting.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('gallery:painting_detail', kwargs={'slug': self.slug})
    
    @property
    def primary_image(self):
        """Get the primary image or the first image"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()
    
    @property
    def is_available(self):
        return self.status == 'available' and self.is_active
    
    @property
    def status_display_class(self):
        """CSS class for status badge"""
        return {
            'available': 'bg-green-100 text-green-800',
            'sold': 'bg-red-100 text-red-800',
            'not_for_sale': 'bg-gray-100 text-gray-800',
        }.get(self.status, 'bg-gray-100 text-gray-800')


class PaintingImage(models.Model):
    """Image for a painting (multiple images per painting)"""
    
    painting = models.ForeignKey(
        Painting, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='Toile'
    )
    image = models.ImageField('Image', upload_to=painting_image_upload_to)
    alt_text = models.CharField('Texte alternatif', max_length=200, blank=True)
    is_primary = models.BooleanField('Image principale', default=False)
    order = models.PositiveIntegerField('Ordre', default=0)
    
    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['-is_primary', 'order']
    
    def __str__(self):
        return f"Image {self.order} - {self.painting.title}"
    
    def save(self, *args, **kwargs):
        # If this is set as primary, unset others
        if self.is_primary:
            PaintingImage.objects.filter(
                painting=self.painting, 
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)









