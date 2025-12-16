from django.db import models


class WordPressHoneypotAttempt(models.Model):
    """Record of WordPress honeypot access attempts"""

    ip_address = models.GenericIPAddressField('Adresse IP')
    user_agent = models.TextField('User Agent', blank=True)
    url_attempted = models.CharField('URL tentée', max_length=200)
    created_at = models.DateTimeField('Date', auto_now_add=True)

    class Meta:
        verbose_name = 'Tentative WordPress'
        verbose_name_plural = 'Tentatives WordPress'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ip_address} - {self.url_attempted} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

