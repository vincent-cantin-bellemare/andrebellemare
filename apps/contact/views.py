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
        try:
            message = form.save(commit=False)
            message.message_type = 'contact'
            message.ip_address = self.get_client_ip()
            message.save()
            
            # Send email notification (fail silently - don't break form submission)
            self.send_notification_email(message)
            
            return super().form_valid(form)
        except Exception as e:
            # If save fails, add error to form
            form.add_error(None, 'Une erreur est survenue lors de l\'envoi de votre message. Veuillez réessayer.')
            return self.form_invalid(form)
    
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
                ['cantinbellemare@gmail.com', 'andrebellemare@live.com'],
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
        
        try:
            message.save()
            
            # Send email notification (fail silently - don't break form submission)
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
                    ['cantinbellemare@gmail.com', 'andrebellemare@live.com'],
                    fail_silently=True,
                )
            except Exception:
                pass  # Email failure doesn't break the form submission
            
            return JsonResponse({
                'success': True,
                'message': 'Votre demande a été envoyée avec succès! L\'artiste vous contactera sous peu.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error_message': 'Une erreur est survenue lors de l\'envoi de votre demande. Veuillez réessayer.'
            }, status=500)
    
    # Format errors for display
    error_messages = []
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                field_label = {
                    'name': 'Nom',
                    'email': 'Courriel',
                    'phone': 'Téléphone',
                    'message': 'Message',
                }.get(field, field)
                error_messages.append(f"{field_label}: {error}")
    
    return JsonResponse({
        'success': False,
        'errors': form.errors,
        'error_message': ' '.join(error_messages) if error_messages else 'Une erreur est survenue lors de la validation du formulaire.'
    }, status=400)




