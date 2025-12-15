from django.contrib import admin
from django.utils.html import format_html

from .models import ContactMessage, FAQ, Testimonial, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message_type', 'painting_link', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_archived', 'created_at']
    list_editable = ['is_read']
    search_fields = ['name', 'email', 'message', 'phone']
    readonly_fields = ['name', 'email', 'phone', 'message', 'message_type', 'painting', 'created_at', 'ip_address']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contact', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('message_type', 'message', 'painting')
        }),
        ('Statut', {
            'fields': ('is_read', 'is_archived')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def painting_link(self, obj):
        if obj.painting:
            return format_html(
                '<a href="/alexandre/gallery/painting/{}/change/">{}</a>',
                obj.painting.pk,
                obj.painting.title
            )
        return '-'
    painting_link.short_description = 'Toile'
    
    def has_add_permission(self, request):
        return False


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_location', 'rating_stars', 'is_active', 'created_at']
    list_editable = ['is_active']
    list_filter = ['is_active', 'rating']
    search_fields = ['author_name', 'author_location', 'content']
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #fbbf24;">{}</span>', stars)
    rating_stars.short_description = 'Note'


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'video_url']
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


# Customize admin site
admin.site.site_header = 'André Bellemare - Administration'
admin.site.site_title = 'André Bellemare Admin'
admin.site.index_title = 'Gestion du site'



