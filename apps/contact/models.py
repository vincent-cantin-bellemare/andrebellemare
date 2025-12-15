from django.db import models


class ContactMessage(models.Model):
    """Contact form message or purchase inquiry"""
    
    MESSAGE_TYPES = [
        ('contact', 'Contact général'),
        ('purchase', 'Demande d\'achat'),
    ]
    
    # Contact info
    name = models.CharField('Nom', max_length=100)
    email = models.EmailField('Courriel')
    phone = models.CharField('Téléphone', max_length=20, blank=True)
    
    # Message
    message = models.TextField('Message')
    message_type = models.CharField('Type', max_length=20, choices=MESSAGE_TYPES, default='contact')
    
    # Related painting (for purchase inquiries)
    painting = models.ForeignKey(
        'gallery.Painting',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name='Toile concernée'
    )
    
    # Status
    is_read = models.BooleanField('Lu', default=False)
    is_archived = models.BooleanField('Archivé', default=False)
    
    # Metadata
    created_at = models.DateTimeField('Reçu le', auto_now_add=True)
    ip_address = models.GenericIPAddressField('Adresse IP', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_message_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class FAQ(models.Model):
    """Frequently Asked Questions"""
    
    question = models.CharField('Question', max_length=300)
    answer = models.TextField('Réponse')
    order = models.PositiveIntegerField('Ordre', default=0)
    is_active = models.BooleanField('Actif', default=True)
    
    class Meta:
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        ordering = ['order']
    
    def __str__(self):
        return self.question


class Testimonial(models.Model):
    """Client testimonials"""
    
    author_name = models.CharField('Nom', max_length=100)
    author_location = models.CharField('Ville', max_length=100, blank=True)
    content = models.TextField('Témoignage')
    rating = models.PositiveIntegerField('Note', default=5, help_text='Note sur 5')
    is_active = models.BooleanField('Actif', default=True)
    created_at = models.DateTimeField('Date', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Témoignage'
        verbose_name_plural = 'Témoignages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.author_name} - {self.author_location}"


class SiteSettings(models.Model):
    """Site-wide settings (singleton)"""
    
    # Video
    video_url = models.URLField('URL vidéo (YouTube/Vimeo)', blank=True, help_text='URL de la vidéo de présentation')
    
    # SEO
    meta_description = models.TextField('Meta description', blank=True, max_length=160)
    meta_keywords = models.CharField('Mots-clés', max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Paramètres du site'
        verbose_name_plural = 'Paramètres du site'
    
    def __str__(self):
        return 'Paramètres du site'
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Get or create the settings instance"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj



