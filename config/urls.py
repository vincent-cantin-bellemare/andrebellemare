"""
URL configuration for andrebellemare project.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from apps.core.sitemaps import StaticViewSitemap, PaintingSitemap, CategorySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'paintings': PaintingSitemap,
    'categories': CategorySitemap,
}

urlpatterns = [
    # Admin at /alexandre/
    path('alexandre/', admin.site.urls),
    
    # Apps
    path('', include('apps.core.urls')),
    path('', include('apps.gallery.urls')),
    path('', include('apps.contact.urls')),
    
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve media files (always, for development)
# In production, configure nginx/apache to serve /media/ directly
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar (only in DEBUG mode)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns




