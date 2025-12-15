from django.contrib import admin
from django.utils.html import format_html
from sorl.thumbnail import get_thumbnail

from .models import Category, Finish, Painting, PaintingImage


class PaintingImageInline(admin.TabularInline):
    """Inline admin for painting images"""
    model = PaintingImage
    extra = 1
    fields = ['image', 'image_preview', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            try:
                thumb = get_thumbnail(obj.image, '100x100', crop='center', quality=85)
                return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />', thumb.url)
            except Exception:
                return format_html('<img src="{}" width="100" height="100" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Aperçu'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'painting_count', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def painting_count(self, obj):
        return obj.painting_count
    painting_count.short_description = 'Toiles'


@admin.register(Finish)
class FinishAdmin(admin.ModelAdmin):
    list_display = ['name', 'painting_count']
    search_fields = ['name']
    
    def painting_count(self, obj):
        return obj.paintings.count()
    painting_count.short_description = 'Toiles'


@admin.register(Painting)
class PaintingAdmin(admin.ModelAdmin):
    list_display = ['thumbnail_preview', 'sku', 'title', 'category', 'price_cad', 'status', 'is_active', 'is_featured']
    list_display_links = ['sku', 'title']
    list_filter = ['status', 'is_active', 'is_featured', 'category', 'finish']
    list_editable = ['is_active', 'is_featured', 'status']
    search_fields = ['sku', 'title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PaintingImageInline]
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('sku', 'title', 'slug', 'description')
        }),
        ('Prix et dimensions', {
            'fields': ('price_cad', 'dimensions')
        }),
        ('Catégorisation', {
            'fields': ('category', 'finish')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_featured', 'status')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thumbnail_preview(self, obj):
        primary = obj.primary_image
        if primary and primary.image:
            try:
                thumb = get_thumbnail(primary.image, '60x60', crop='center', quality=85)
                return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />', thumb.url)
            except Exception:
                return format_html('<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />', primary.image.url)
        return '-'
    thumbnail_preview.short_description = 'Image'


@admin.register(PaintingImage)
class PaintingImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'painting', 'is_primary', 'order']
    list_filter = ['is_primary', 'painting__category']
    list_editable = ['is_primary', 'order']
    search_fields = ['painting__title', 'painting__sku']
    
    def image_preview(self, obj):
        if obj.image:
            try:
                thumb = get_thumbnail(obj.image, '80x80', crop='center', quality=85)
                return format_html('<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px;" />', thumb.url)
            except Exception:
                return format_html('<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Aperçu'









