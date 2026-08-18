from django import forms

from accounts.forms import BootstrapFormMixin
from .models import Report


class ReportForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        self.fields['description'].widget.attrs['placeholder'] = (
            'Describe what happened — include dates, what was agreed, and what went wrong.'
        )
