from django import forms

from accounts.forms import BootstrapFormMixin
from .models import Review

RATING_CHOICES = [(5, '5 — Excellent'), (4, '4 — Good'), (3, '3 — Average'), (2, '2 — Below Average'), (1, '1 — Poor')]


class ReviewForm(BootstrapFormMixin, forms.ModelForm):
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        self.fields['rating'].widget.attrs['class'] = ''
        self.fields['comment'].widget.attrs['placeholder'] = 'Share details of your experience (optional)'
        self.fields['comment'].required = False
