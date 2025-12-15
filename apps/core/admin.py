from django.contrib import admin
from django.utils.html import format_html

from .models import WordPressHoneypotAttempt


@admin.register(WordPressHoneypotAttempt)
class WordPressHoneypotAttemptAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'url_attempted', 'user_agent_short', 'created_at']
    list_filter = ['url_attempted', 'created_at']
    search_fields = ['ip_address', 'user_agent', 'url_attempted']
    readonly_fields = ['ip_address', 'user_agent', 'url_attempted', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Tentative', {
            'fields': ('url_attempted', 'ip_address', 'user_agent', 'created_at')
        }),
    )
    
    def user_agent_short(self, obj):
        """Display shortened user agent"""
        if obj.user_agent:
            # Truncate to 60 characters
            ua = obj.user_agent[:60]
            if len(obj.user_agent) > 60:
                ua += '...'
            return ua
        return '—'
    user_agent_short.short_description = 'User Agent'
    
    def has_add_permission(self, request):
        """Disable manual addition of attempts"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of attempts"""
        return False
