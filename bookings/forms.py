from datetime import date

from django import forms

from accounts.forms import BootstrapFormMixin
from .models import Booking


class BookingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service_date', 'service_time', 'address', 'notes', 'preferred_payment_method']
        widgets = {
            'service_date': forms.DateInput(attrs={'type': 'date'}),
            'service_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'preferred_payment_method': forms.RadioSelect,
        }

    def __init__(self, *args, provider=None, **kwargs):
        self.provider = provider
        super().__init__(*args, **kwargs)
        self._style_fields()
        self.fields['address'].widget.attrs['placeholder'] = 'Full address where the service is needed'
        self.fields['notes'].widget.attrs['placeholder'] = 'Anything the provider should know (optional)'
        self.fields['notes'].required = False
        self.fields['preferred_payment_method'].widget.attrs['class'] = 'btn-check'
        self.fields['preferred_payment_method'].widget.attrs['autocomplete'] = 'off'
        self.fields['preferred_payment_method'].label = 'Payment Method'
        self.fields['preferred_payment_method'].help_text = (
            "Chosen now so it's ready when the job is marked complete — you're not charged today."
        )

    def clean_service_date(self):
        service_date = self.cleaned_data['service_date']
        if service_date < date.today():
            raise forms.ValidationError('Please choose a date that is today or in the future.')
        if self.provider:
            day_abbr = service_date.strftime('%a')
            if day_abbr not in self.provider.availability_day_list:
                available = ', '.join(self.provider.availability_day_list) or 'no days currently set'
                raise forms.ValidationError(
                    f'{self.provider.display_name} is not available on {service_date.strftime("%A")}s. '
                    f'Available days: {available}.'
                )
        return service_date

    def clean_service_time(self):
        service_time = self.cleaned_data['service_time']
        if self.provider and self.provider.availability_start and self.provider.availability_end:
            if not (self.provider.availability_start <= service_time <= self.provider.availability_end):
                raise forms.ValidationError(
                    f'{self.provider.display_name} is available between '
                    f'{self.provider.availability_start.strftime("%I:%M %p")} and '
                    f'{self.provider.availability_end.strftime("%I:%M %p")}.'
                )
        return service_time
