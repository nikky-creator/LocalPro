from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class BootstrapFormMixin:
    """Applies Bootstrap 5 form-control/form-select classes to every field automatically."""

    def _style_fields(self):
        for name, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = (existing + ' form-check-input').strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs['class'] = (existing + ' form-select').strip()
            else:
                widget.attrs['class'] = (existing + ' form-control').strip()
            if field.help_text and 'placeholder' not in widget.attrs:
                pass


class StyledAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'Username', 'autofocus': True})
        self.fields['password'].widget.attrs.update({'placeholder': 'Password'})
        self._style_fields()


class CustomerRegisterForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    city = forms.CharField(max_length=100, required=True)
    address = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'city', 'address', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        placeholders = {
            'first_name': 'First name', 'last_name': 'Last name', 'username': 'Choose a username',
            'email': 'you@example.com', 'phone': '10-digit mobile number', 'city': 'Your city',
            'address': 'Street, area, landmark (optional)',
            'password1': 'Create a password', 'password2': 'Confirm password',
        }
        for name, text in placeholders.items():
            self.fields[name].widget.attrs['placeholder'] = text

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = phone.replace('+', '').replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError('Enter a valid phone number (at least 10 digits).')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = Profile.ROLE_CUSTOMER
            profile.phone = self.cleaned_data['phone']
            profile.city = self.cleaned_data['city']
            profile.address = self.cleaned_data.get('address', '')
            profile.save()
        return user


class ProviderRegisterForm(BootstrapFormMixin, UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        placeholders = {
            'first_name': 'First name', 'last_name': 'Last name', 'username': 'Choose a username',
            'email': 'you@example.com', 'phone': '10-digit mobile number',
            'password1': 'Create a password', 'password2': 'Confirm password',
        }
        for name, text in placeholders.items():
            self.fields[name].widget.attrs['placeholder'] = text

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = phone.replace('+', '').replace(' ', '').replace('-', '')
        if not digits.isdigit() or len(digits) < 10:
            raise forms.ValidationError('Enter a valid phone number (at least 10 digits).')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = Profile.ROLE_PROVIDER
            profile.phone = self.cleaned_data['phone']
            profile.save()
        return user


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'avatar']
        widgets = {'address': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_fields()
        self.fields['avatar'].widget.attrs['data-preview-target'] = '#avatarPreview'
        self.fields['avatar'].widget.attrs['accept'] = 'image/png,image/jpeg,image/webp'

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            if avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image must be smaller than 5MB.')
            valid = ('.jpg', '.jpeg', '.png', '.webp')
            if not str(avatar.name).lower().endswith(valid):
                raise forms.ValidationError('Only JPG, PNG, or WEBP images are allowed.')
        return avatar
