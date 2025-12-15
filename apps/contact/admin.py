from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from .models import ContactMessage, FAQ, Testimonial, SiteSettings


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message_type', 'painting_link', 'is_read', 'email_status_display', 'last_email_datetime', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_archived', 'last_email_status', 'created_at']
    list_editable = ['is_read']
    search_fields = ['name', 'email', 'message', 'phone']
    readonly_fields = ['name', 'email', 'phone', 'message', 'message_type', 'painting', 'created_at', 'ip_address', 
                       'last_email_status', 'last_email_datetime', 'last_email_error', 'last_email_traceback']
    date_hierarchy = 'created_at'
    actions = ['resend_notification_email']
    
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
        ('Statut Email', {
            'fields': ('last_email_status', 'last_email_datetime', 'last_email_error', 'last_email_traceback'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    def email_status_display(self, obj):
        """Display email status with color coding"""
        if obj.last_email_status is None:
            return format_html('<span style="color: #6b7280;">—</span>')
        elif obj.last_email_status is True:
            return format_html('<span style="color: #10b981;">✓ Succès</span>')
        else:
            return format_html('<span style="color: #ef4444;">✗ Échec</span>')
    email_status_display.short_description = 'Email'
    
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
    
    def resend_notification_email(self, request, queryset):
        """Action admin pour renvoyer les emails de notification"""
        count = 0
        errors = []
        
        for message in queryset:
            try:
                email_sent, email_error = message.send_notification_email(fail_silently=False)
                if email_sent:
                    count += 1
                else:
                    errors.append(f'{message.name}: {email_error or "Erreur inconnue"}')
            except Exception as e:
                errors.append(f'{message.name}: {str(e)}')
        
        if count > 0:
            self.message_user(
                request,
                f'{count} email(s) renvoyé(s) avec succès.',
                level=messages.SUCCESS
            )
        
        if errors:
            for error in errors:
                self.message_user(
                    request,
                    f'Erreur lors de l\'envoi pour {error}',
                    level=messages.ERROR
                )
    
    resend_notification_email.short_description = 'Renvoyer l\'email de notification'


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








