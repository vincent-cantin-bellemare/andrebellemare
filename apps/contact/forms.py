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
                'placeholder': 'Message optionnel...',
                'rows': 3,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['message'].required = False
        self.fields['phone'].required = False
        # Remove HTML required attribute to rely on backend validation
        # Fields are still required at the form level, but HTML5 validation is disabled
        for field_name in ['name', 'email']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.pop('required', None)









