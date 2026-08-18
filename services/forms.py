from django import forms

from accounts.forms import BootstrapFormMixin
from .models import Provider

DAY_CHOICES = [
    ('Mon', 'Mon'), ('Tue', 'Tue'), ('Wed', 'Wed'), ('Thu', 'Thu'),
    ('Fri', 'Fri'), ('Sat', 'Sat'), ('Sun', 'Sun'),
]


class ProviderProfileForm(BootstrapFormMixin, forms.ModelForm):
    availability_day_choices = forms.MultipleChoiceField(
        choices=DAY_CHOICES, widget=forms.CheckboxSelectMultiple, required=True,
        label='Available days'
    )

    class Meta:
        model = Provider
        fields = [
            'category', 'business_name', 'bio', 'experience_years', 'price_per_hour',
            'location', 'city', 'latitude', 'longitude', 'photo',
            'availability_start', 'availability_end', 'is_available',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'availability_start': forms.TimeInput(attrs={'type': 'time'}),
            'availability_end': forms.TimeInput(attrs={'type': 'time'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.availability_days:
            self.fields['availability_day_choices'].initial = self.instance.availability_day_list
        self._style_fields()
        self.fields['availability_day_choices'].widget.attrs['class'] = ''
        self.fields['photo'].widget.attrs['data-preview-target'] = '#photoPreview'
        self.fields['photo'].widget.attrs['accept'] = 'image/png,image/jpeg,image/webp'
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['latitude'].widget.attrs['id'] = 'id_latitude'
        self.fields['longitude'].widget.attrs['id'] = 'id_longitude'
        placeholders = {
            'business_name': 'e.g. Ramesh Electrical Works',
            'bio': 'Describe your skills, specialties, and what makes your service great...',
            'location': 'e.g. Governorpet, MG Road',
            'city': 'e.g. Vijayawada',
        }
        for name, text in placeholders.items():
            if name in self.fields:
                self.fields[name].widget.attrs['placeholder'] = text

    def clean_price_per_hour(self):
        price = self.cleaned_data['price_per_hour']
        if price <= 0:
            raise forms.ValidationError('Price must be greater than 0.')
        if price > 100000:
            raise forms.ValidationError('That price looks too high — please double-check.')
        return price

    def clean_experience_years(self):
        years = self.cleaned_data['experience_years']
        if years > 70:
            raise forms.ValidationError('Please enter a realistic number of years.')
        return years

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size'):
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be smaller than 5MB.')
            valid = ('.jpg', '.jpeg', '.png', '.webp')
            if not str(photo.name).lower().endswith(valid):
                raise forms.ValidationError('Only JPG, PNG, or WEBP images are allowed.')
        return photo

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('availability_start')
        end = cleaned.get('availability_end')
        if start and end and start >= end:
            raise forms.ValidationError('Availability end time must be after the start time.')
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.availability_days = ','.join(self.cleaned_data['availability_day_choices'])
        if commit:
            instance.save()
        return instance
