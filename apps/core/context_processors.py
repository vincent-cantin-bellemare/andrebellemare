from django.conf import settings

from apps.gallery.models import Category


def site_settings(request):
    """Add site settings to all templates"""
    return {
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'contact_address': settings.CONTACT_ADDRESS,
        'contact_phone': settings.CONTACT_PHONE,
        'contact_facebook': settings.CONTACT_FACEBOOK,
        'all_categories': Category.objects.all(),
        'MEDIA_URL': settings.MEDIA_URL,
    }



