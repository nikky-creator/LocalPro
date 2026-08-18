import re

from django import forms

from accounts.forms import BootstrapFormMixin
from .models import Payment


class PaymentForm(BootstrapFormMixin, forms.Form):
    """
    Simulated checkout form. Only `method` is ever saved to the Payment
    record — card_number/card_cvv/upi_id exist purely for on-screen realism
    and validation, and are discarded after this form is processed.
    """
    method = forms.ChoiceField(choices=Payment.METHOD_CHOICES, widget=forms.RadioSelect, initial=Payment.METHOD_CARD)
    card_number = forms.CharField(required=False, max_length=19)
    card_name = forms.CharField(required=False, max_length=100)
    card_expiry = forms.CharField(required=False, max_length=5)
    card_cvv = forms.CharField(required=False, max_length=4)
    upi_id = forms.CharField(required=False, max_length=50)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        self.fields['method'].widget.attrs.update({'class': 'btn-check', 'autocomplete': 'off'})
        self.fields['card_number'].widget.attrs.update({'placeholder': '1234 5678 9012 3456', 'autocomplete': 'off', 'maxlength': 19})
        self.fields['card_name'].widget.attrs['placeholder'] = 'Name on card'
        self.fields['card_expiry'].widget.attrs.update({'placeholder': 'MM/YY', 'autocomplete': 'off', 'maxlength': 5})
        self.fields['card_cvv'].widget.attrs.update({'placeholder': 'CVV', 'autocomplete': 'off', 'maxlength': 4})
        self.fields['upi_id'].widget.attrs['placeholder'] = 'yourname@upi'

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('method')

        if method == Payment.METHOD_CARD:
            digits = re.sub(r'\s+', '', cleaned.get('card_number', ''))
            if not digits.isdigit() or not (13 <= len(digits) <= 19):
                self.add_error('card_number', 'Enter a valid card number.')
            if not cleaned.get('card_name', '').strip():
                self.add_error('card_name', 'Enter the name on the card.')
            if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', cleaned.get('card_expiry', '').strip()):
                self.add_error('card_expiry', 'Use MM/YY format.')
            cvv = cleaned.get('card_cvv', '').strip()
            if not cvv.isdigit() or not (3 <= len(cvv) <= 4):
                self.add_error('card_cvv', 'Enter a valid CVV.')

        elif method == Payment.METHOD_UPI:
            upi = cleaned.get('upi_id', '').strip()
            if '@' not in upi or len(upi) < 5:
                self.add_error('upi_id', 'Enter a valid UPI ID, e.g. yourname@bank.')

        return cleaned
