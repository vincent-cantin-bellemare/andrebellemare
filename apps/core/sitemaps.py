from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.gallery.models import Painting, Category


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 0.8
    changefreq = 'monthly'
    
    def items(self):
        return ['core:home', 'core:about', 'core:delivery', 'core:terms', 'core:faq', 'contact:contact']
    
    def location(self, item):
        return reverse(item)


class PaintingSitemap(Sitemap):
    """Sitemap for paintings"""
    priority = 0.9
    changefreq = 'weekly'
    
    def items(self):
        return Painting.objects.filter(is_active=True)
    
    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    """Sitemap for categories"""
    priority = 0.7
    changefreq = 'weekly'
    
    def items(self):
        return Category.objects.all()
