from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def validate_image_file(file):
    """Extra server-side safety net on top of form-level validation."""
    from django.core.exceptions import ValidationError
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    name = file.name.lower()
    if not any(name.endswith(e) for e in valid_extensions):
        raise ValidationError('Unsupported file type. Please upload a JPG, PNG, or WEBP image.')
    if file.size > 5 * 1024 * 1024:
        raise ValidationError('Image file too large ( max 5MB ).')


class Profile(models.Model):
    ROLE_CUSTOMER = 'customer'
    ROLE_PROVIDER = 'provider'
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, _('Customer')),
        (ROLE_PROVIDER, _('Service Provider')),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=15, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True, validators=[validate_image_file]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_role_display()})'

    def get_absolute_url(self):
        return reverse('accounts:profile')

    @property
    def is_customer(self):
        return self.role == self.ROLE_CUSTOMER

    @property
    def is_provider(self):
        return self.role == self.ROLE_PROVIDER

    @property
    def initials(self):
        name = self.user.get_full_name() or self.user.username
        parts = [p for p in name.split() if p]
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper() if name else '??'
