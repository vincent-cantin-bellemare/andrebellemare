from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom complet',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'votre@courriel.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '514-555-1234',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Votre message...',
                'rows': 5,
            }),
        }


class PurchaseInquiryForm(forms.ModelForm):
    """Purchase inquiry form (modal)"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Votre nom complet',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'votre@courriel.com',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '514-555-1234',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Message optionnel...',
                'rows': 3,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].required = False
        self.fields['phone'].required = False

