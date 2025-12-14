from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

from apps.gallery.models import Painting, Category
from apps.contact.models import FAQ, Testimonial


class HomeView(TemplateView):
    """Home page with featured paintings"""
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_paintings'] = Painting.objects.filter(
            is_active=True, 
            is_featured=True
        ).select_related('category', 'finish').prefetch_related('images')[:12]
        context['categories'] = Category.objects.all()
        context['testimonials'] = Testimonial.objects.filter(is_active=True)[:3]
        return context


class AboutView(TemplateView):
    """About the artist page"""
    template_name = 'pages/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.contact.models import SiteSettings
        context['settings'] = SiteSettings.get_settings()
        return context


class DeliveryView(TemplateView):
    """Delivery and returns policy page"""
    template_name = 'pages/delivery.html'


class TermsView(TemplateView):
    """Terms and conditions page"""
    template_name = 'pages/terms.html'


class FAQView(TemplateView):
    """FAQ page"""
    template_name = 'pages/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faqs'] = FAQ.objects.filter(is_active=True)
        return context


def robots_txt(request):
    """Generate robots.txt"""
    lines = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

