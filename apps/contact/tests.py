"""
Tests for contact app
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.core import mail
from django.urls import reverse

from apps.contact.models import ContactMessage
from apps.contact.forms import ContactForm
from apps.gallery.models import Painting


class ContactMessageModelTest(TestCase):
    """Tests for ContactMessage model"""
    
    def setUp(self):
        """Set up test data"""
        self.message_data = {
            'name': 'Jean Dupont',
            'email': 'jean.dupont@example.com',
            'phone': '514-555-1234',
            'message': 'Bonjour, j\'aimerais en savoir plus sur vos toiles.',
            'message_type': 'contact',
        }
    
    def test_contact_message_creation(self):
        """Test creating a contact message"""
        message = ContactMessage.objects.create(**self.message_data)
        self.assertEqual(message.name, 'Jean Dupont')
        self.assertEqual(message.email, 'jean.dupont@example.com')
        self.assertEqual(message.message_type, 'contact')
        self.assertIsNotNone(message.created_at)
        self.assertFalse(message.is_read)
        self.assertFalse(message.is_archived)
    
    def test_contact_message_without_phone(self):
        """Test creating a contact message without phone"""
        data = self.message_data.copy()
        del data['phone']
        message = ContactMessage.objects.create(**data)
        self.assertEqual(message.phone, '')
    
    def test_contact_message_str(self):
        """Test string representation of contact message"""
        message = ContactMessage.objects.create(**self.message_data)
        str_repr = str(message)
        self.assertIn('Jean Dupont', str_repr)
        self.assertIn('Contact général', str_repr)
    
    def test_send_notification_email_contact(self):
        """Test sending notification email for contact message"""
        message = ContactMessage.objects.create(**self.message_data)
        
        # Clear mail outbox
        mail.outbox = []
        
        # Send email
        result = message.send_notification_email(fail_silently=False)
        
        # Check email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nouveau message de Jean Dupont', mail.outbox[0].subject)
        self.assertIn('jean.dupont@example.com', mail.outbox[0].body)
    
    def test_send_notification_email_purchase(self):
        """Test sending notification email for purchase inquiry"""
        # Create a painting
        painting = Painting.objects.create(
            sku='TEST-001',
            title='Test Painting',
            price_cad=Decimal('500.00'),
            dimensions='24" x 36"',
            is_active=True,
        )
        
        # Create purchase message
        message = ContactMessage.objects.create(
            name='Marie Tremblay',
            email='marie.tremblay@example.com',
            phone='438-555-5678',
            message='Je suis intéressée par cette toile.',
            message_type='purchase',
            painting=painting,
        )
        
        # Clear mail outbox
        mail.outbox = []
        
        # Send email
        result = message.send_notification_email(fail_silently=False)
        
        # Check email was sent
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Demande d\'achat - Test Painting', mail.outbox[0].subject)
        self.assertIn('Test Painting', mail.outbox[0].body)
        self.assertIn('Marie Tremblay', mail.outbox[0].body)
    
    def test_send_notification_email_fail_silently(self):
        """Test that email failure doesn't raise exception when fail_silently=True"""
        message = ContactMessage.objects.create(**self.message_data)
        
        # Mock send_mail to raise an exception
        with patch('apps.contact.models.send_mail', side_effect=Exception('Email error')):
            result = message.send_notification_email(fail_silently=True)
            self.assertFalse(result)
    
    def test_send_notification_email_raises_when_not_silent(self):
        """Test that email failure raises exception when fail_silently=False"""
        message = ContactMessage.objects.create(**self.message_data)
        
        # Mock send_mail to raise an exception
        with patch('apps.contact.models.send_mail', side_effect=Exception('Email error')):
            with self.assertRaises(Exception):
                message.send_notification_email(fail_silently=False)


class ContactFormViewTest(TestCase):
    """Tests for contact form view"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.url = reverse('contact:contact')
    
    def test_contact_form_saves_to_database(self):
        """Test that contact form saves message to database"""
        form_data = {
            'name': 'Pierre Martin',
            'email': 'pierre.martin@example.com',
            'phone': '514-555-9999',
            'message': 'Bonjour, j\'aimerais vous contacter.',
        }
        
        initial_count = ContactMessage.objects.count()
        
        response = self.client.post(self.url, data=form_data)
        
        # Check redirect to success page
        self.assertEqual(response.status_code, 302)
        self.assertIn('success=1', response.url)
        
        # Check message was saved
        self.assertEqual(ContactMessage.objects.count(), initial_count + 1)
        message = ContactMessage.objects.latest('created_at')
        self.assertEqual(message.name, 'Pierre Martin')
        self.assertEqual(message.email, 'pierre.martin@example.com')
        self.assertEqual(message.message_type, 'contact')
    
    def test_contact_form_with_optional_fields(self):
        """Test contact form with optional phone field"""
        form_data = {
            'name': 'Sophie Lavoie',
            'email': 'sophie.lavoie@example.com',
            'message': 'Message sans téléphone.',
        }
        
        response = self.client.post(self.url, data=form_data)
        
        # Check redirect to success page
        self.assertEqual(response.status_code, 302)
        
        # Check message was saved without phone
        message = ContactMessage.objects.latest('created_at')
        self.assertEqual(message.name, 'Sophie Lavoie')
        self.assertEqual(message.phone, '')
    
    def test_contact_form_sets_message_type(self):
        """Test that contact form sets message_type to 'contact'"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message.',
        }
        
        self.client.post(self.url, data=form_data)
        
        message = ContactMessage.objects.latest('created_at')
        self.assertEqual(message.message_type, 'contact')
    
    def test_contact_form_captures_ip_address(self):
        """Test that contact form captures IP address"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message.',
        }
        
        response = self.client.post(self.url, data=form_data)
        
        message = ContactMessage.objects.latest('created_at')
        # IP should be captured (127.0.0.1 in test environment)
        self.assertIsNotNone(message.ip_address)
    
    def test_contact_form_validation_errors(self):
        """Test that form validation errors are displayed"""
        # Submit form without required fields
        response = self.client.post(self.url, data={})
        
        # Should return form with errors
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
    
    def test_contact_form_error_display_on_save_failure(self):
        """Test that errors are displayed when save fails"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'message': 'Test message.',
        }
        
        # Mock save to raise an exception
        with patch('apps.contact.models.ContactMessage.save', side_effect=Exception('Database error')):
            response = self.client.post(self.url, data=form_data)
            
            # Should return form with error
            self.assertEqual(response.status_code, 200)
            self.assertIn('form', response.context)
            form = response.context['form']
            self.assertTrue(form.non_field_errors)
            self.assertIn('erreur', form.non_field_errors[0].lower())
    
    def test_contact_form_sends_email(self):
        """Test that contact form sends notification email"""
        form_data = {
            'name': 'Email Test',
            'email': 'email@example.com',
            'message': 'Test email sending.',
        }
        
        # Clear mail outbox
        mail.outbox = []
        
        response = self.client.post(self.url, data=form_data)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Nouveau message de Email Test', mail.outbox[0].subject)


class PurchaseInquiryTest(TestCase):
    """Tests for purchase inquiry form"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.painting = Painting.objects.create(
            sku='TEST-002',
            title='Test Painting 2',
            price_cad=Decimal('750.00'),
            dimensions='30" x 40"',
            is_active=True,
        )
        self.url = reverse('contact:purchase_inquiry')
    
    def test_purchase_inquiry_saves_to_database(self):
        """Test that purchase inquiry saves to database"""
        form_data = {
            'painting_id': self.painting.id,
            'name': 'Acheteur Test',
            'email': 'acheteur@example.com',
            'phone': '514-555-0000',
            'message': 'Je veux acheter cette toile.',
        }
        
        initial_count = ContactMessage.objects.count()
        
        response = self.client.post(self.url, data=form_data)
        
        # Check success response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Check message was saved
        self.assertEqual(ContactMessage.objects.count(), initial_count + 1)
        message = ContactMessage.objects.latest('created_at')
        self.assertEqual(message.message_type, 'purchase')
        self.assertEqual(message.painting, self.painting)
        self.assertEqual(message.name, 'Acheteur Test')
    
    def test_purchase_inquiry_sends_email(self):
        """Test that purchase inquiry sends notification email"""
        form_data = {
            'painting_id': self.painting.id,
            'name': 'Email Test 2',
            'email': 'email2@example.com',
            'message': 'Test purchase email.',
        }
        
        # Clear mail outbox
        mail.outbox = []
        
        response = self.client.post(self.url, data=form_data)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Demande d\'achat - Test Painting 2', mail.outbox[0].subject)
    
    def test_purchase_inquiry_error_handling(self):
        """Test that purchase inquiry handles errors gracefully"""
        form_data = {
            'painting_id': self.painting.id,
            'name': 'Error Test',
            'email': 'error@example.com',
            'message': 'Test error handling.',
        }
        
        # Mock save to raise an exception
        with patch('apps.contact.models.ContactMessage.save', side_effect=Exception('Database error')):
            response = self.client.post(self.url, data=form_data)
            
            # Should return error response
            self.assertEqual(response.status_code, 500)
            data = response.json()
            self.assertFalse(data['success'])
            self.assertIn('erreur', data['error_message'].lower())

