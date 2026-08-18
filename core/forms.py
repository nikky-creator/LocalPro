from django import forms

from accounts.forms import BootstrapFormMixin
from .models import ContactMessage


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        placeholders = {
            'name': 'Your name', 'email': 'you@example.com',
            'subject': 'What is this about?', 'message': 'Write your message here...',
        }
        for name, text in placeholders.items():
            self.fields[name].widget.attrs['placeholder'] = text
