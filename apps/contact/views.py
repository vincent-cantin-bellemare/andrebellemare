import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import FormView
from django.http import JsonResponse

from .forms import ContactForm, PurchaseInquiryForm
from .models import ContactMessage
from apps.gallery.models import Painting

logger = logging.getLogger(__name__)


class ContactView(FormView):
    """Contact page with form - supports both regular and AJAX submissions"""
    template_name = 'pages/contact.html'
    form_class = ContactForm
    success_url = '/contact/?success=1'

    def is_ajax(self):
        """Check if request is AJAX"""
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def form_valid(self, form):
        try:
            message = form.save(commit=False)
            message.message_type = 'contact'
            message.ip_address = self.get_client_ip()
            message.save()

            # Send email notification - check if it succeeds
            email_sent, email_error = message.send_notification_email(fail_silently=False)

            # Reload message to get updated email status
            message.refresh_from_db()

            if not email_sent or message.last_email_status is not True:
                # Log the email error for debugging
                logger.error(f'Failed to send contact notification email: {email_error}', exc_info=True)

                error_msg = (
                    'Votre message a été enregistré, mais nous n\'avons pas pu envoyer la notification par courriel. '
                    'L\'artiste sera informé de votre message. Si le problème persiste, contactez-nous directement.'
                )

                if self.is_ajax():
                    return JsonResponse({
                        'success': False,
                        'error_message': error_msg
                    }, status=200)

                form.add_error(None, error_msg)
                return self.form_invalid(form)

            if self.is_ajax():
                return JsonResponse({
                    'success': True,
                    'message': 'Votre message a été envoyé avec succès! Je vous répondrai dans les plus brefs délais.'
                })

            return super().form_valid(form)
        except Exception as e:
            # Log the error for debugging
            logger.error(f'Error saving contact message: {str(e)}', exc_info=True)

            # Check if it's an email error (message was saved but email failed)
            if hasattr(e, '__class__') and ('email' in str(e).lower() or 'send_mail' in str(e).lower()):
                error_msg = (
                    'Votre message a été enregistré, mais nous n\'avons pas pu envoyer la notification par courriel. '
                    'L\'artiste sera informé de votre message. Si le problème persiste, contactez-nous directement.'
                )

                if self.is_ajax():
                    return JsonResponse({
                        'success': False,
                        'error_message': error_msg
                    }, status=200)

                form.add_error(None, error_msg)
                return self.form_invalid(form)

            error_msg = 'Une erreur est survenue lors de l\'envoi de votre message. Veuillez réessayer. Si le problème persiste, contactez-nous directement.'

            if self.is_ajax():
                return JsonResponse({
                    'success': False,
                    'error_message': error_msg
                }, status=500)

            form.add_error(None, error_msg)
            return self.form_invalid(form)

    def form_invalid(self, form):
        if self.is_ajax():
            # Format errors for display
            error_messages = []
            if form.errors:
                for field, errors in form.errors.items():
                    if field == '__all__':
                        error_messages.extend(errors)
                    else:
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

        return super().form_invalid(form)

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')

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

            # Send email notification - check if it succeeds
            email_sent, email_error = message.send_notification_email(fail_silently=False)

            # Reload message to get updated email status
            message.refresh_from_db()

            if not email_sent or message.last_email_status is not True:
                # Log the email error for debugging
                logger.error(f'Failed to send purchase inquiry notification email: {email_error}', exc_info=True)

                # Message is saved but email failed - inform user
                return JsonResponse({
                    'success': False,
                    'error_message': 'Votre demande a été enregistrée, mais nous n\'avons pas pu envoyer la notification par courriel. '
                                   'L\'artiste sera informé de votre demande. Si le problème persiste, contactez-nous directement.'
                }, status=200)  # 200 because message was saved successfully

            return JsonResponse({
                'success': True,
                'message': 'Votre demande a été envoyée avec succès! L\'artiste vous contactera sous peu.'
            })
        except Exception as e:
            # Log the error for debugging
            logger.error(f'Error saving purchase inquiry: {str(e)}', exc_info=True)

            # Check if it's an email error (message was saved but email failed)
            if hasattr(e, '__class__') and 'email' in str(e).lower():
                # Message is saved but email failed - inform user
                return JsonResponse({
                    'success': False,
                    'error_message': 'Votre demande a été enregistrée, mais nous n\'avons pas pu envoyer la notification par courriel. '
                                   'L\'artiste sera informé de votre demande. Si le problème persiste, contactez-nous directement.'
                }, status=200)  # 200 because message was saved successfully

            return JsonResponse({
                'success': False,
                'error_message': 'Une erreur est survenue lors de l\'envoi de votre demande. Veuillez réessayer. Si le problème persiste, contactez-nous directement.'
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
