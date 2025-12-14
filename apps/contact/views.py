from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import FormView
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .forms import ContactForm, PurchaseInquiryForm
from .models import ContactMessage
from apps.gallery.models import Painting


class ContactView(FormView):
    """Contact page with form"""
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = '/contact/?success=1'
    
    def form_valid(self, form):
        message = form.save(commit=False)
        message.message_type = 'contact'
        message.ip_address = self.get_client_ip()
        message.save()
        
        # Send email notification
        self.send_notification_email(message)
        
        return super().form_valid(form)
    
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')
    
    def send_notification_email(self, message):
        """Send email notification to artist"""
        try:
            subject = f'[André Bellemare] Nouveau message de {message.name}'
            body = render_to_string('emails/contact_notification.html', {
                'message': message,
            })
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
        except Exception:
            pass  # Don't break form submission if email fails
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['success'] = self.request.GET.get('success')
        return context


def purchase_inquiry(request):
    """Handle purchase inquiry form (AJAX)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    painting_id = request.POST.get('painting_id')
    painting = get_object_or_404(Painting, pk=painting_id, is_active=True)
    
    form = PurchaseInquiryForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.painting = painting
        message.message_type = 'purchase'
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            message.ip_address = x_forwarded_for.split(',')[0]
        else:
            message.ip_address = request.META.get('REMOTE_ADDR')
        
        message.save()
        
        # Send email notification
        try:
            subject = f'[André Bellemare] Demande d\'achat - {painting.title}'
            body = render_to_string('emails/purchase_notification.html', {
                'message': message,
                'painting': painting,
            })
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],
                fail_silently=True,
            )
        except Exception:
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Votre demande a été envoyée avec succès! L\'artiste vous contactera sous peu.'
        })
    
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)

