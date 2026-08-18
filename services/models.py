import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.text import slugify

# Approximate town/city centers used as a fallback map location for
# providers who haven't pinned their exact coordinates. Extend this as more
# cities are added.
CITY_COORDS = {
    'vijayawada': (16.5062, 80.6480),
    'guntur': (16.3067, 80.4365),
    'vishakhapatnam': (17.6868, 83.2185),
    'visakhapatnam': (17.6868, 83.2185),
    'rajahmundry': (17.0005, 81.8040),
    'eluru': (16.7107, 81.0952),
}
DEFAULT_CITY_COORDS = (16.5062, 80.6480)  # Vijayawada, used if city is unrecognized


def _deterministic_jitter(seed_key, spread=0.025):
    """
    Small, stable pseudo-random offset (in degrees, ~spread*111km) derived
    from a string key, so a provider's fallback map pin doesn't jump around
    between requests/deploys.
    """
    digest = hashlib.md5(seed_key.encode('utf-8')).hexdigest()
    x = (int(digest[:8], 16) / 0xFFFFFFFF) * 2 - 1
    y = (int(digest[8:16], 16) / 0xFFFFFFFF) * 2 - 1
    return x * spread, y * spread


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=110, unique=True, blank=True)
    icon = models.CharField(
        max_length=50, default='fa-solid fa-toolbox',
        help_text='Font Awesome class, e.g. "fa-solid fa-bolt"'
    )
    description = models.CharField(max_length=255, blank=True)
    color = models.CharField(
        max_length=20, default='navy',
        help_text='Brand accent key: navy, green, orange, blue, gold'
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Service Categories'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('services:provider_list') + f'?category={self.slug}'

    @property
    def provider_count(self):
        return self.providers.filter(is_available=True).count()


class Provider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='provider_profile')
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.PROTECT, related_name='providers'
    )
    business_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(
        max_length=1000, blank=True,
        help_text='Tell customers about your experience and specialties.'
    )
    experience_years = models.PositiveIntegerField(default=0)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    location = models.CharField(max_length=150, help_text='Area / locality, e.g. "MG Road"')
    city = models.CharField(max_length=100)
    latitude = models.FloatField(
        null=True, blank=True, help_text='Optional: pin your exact location so nearby customers find you.'
    )
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to='provider_photos/', blank=True, null=True)

    is_available = models.BooleanField(default=True, help_text='Currently accepting new bookings')
    availability_days = models.CharField(
        max_length=255, blank=True, default='Mon,Tue,Wed,Thu,Fri,Sat',
        help_text='Comma-separated days, e.g. Mon,Tue,Wed'
    )
    availability_start = models.TimeField(default='09:00')
    availability_end = models.TimeField(default='18:00')

    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Not a DB field — set on individual instances by services.views.provider_list
    # when the visitor's location is known, so templates can safely check
    # `provider.distance_km is not None` without an AttributeError either way.
    distance_km = None

    class Meta:
        ordering = ['-is_verified', '-created_at']

    def __str__(self):
        return self.business_name or self.user.get_full_name() or self.user.username

    def get_absolute_url(self):
        return reverse('services:provider_detail', args=[self.pk])

    @property
    def display_name(self):
        return self.business_name or self.user.get_full_name() or self.user.username

    @property
    def average_rating(self):
        result = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result else 0

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def completed_jobs(self):
        return self.bookings.filter(status='completed').count()

    @property
    def availability_day_list(self):
        return [d.strip() for d in self.availability_days.split(',') if d.strip()]

    @property
    def map_coords(self):
        """
        (lat, lng) to show on a map. Uses the provider's own pinned
        coordinates if set, otherwise falls back to a stable point near
        their city center so every provider is still visible on the map.
        """
        if self.latitude is not None and self.longitude is not None:
            return (self.latitude, self.longitude)
        base_lat, base_lng = CITY_COORDS.get(self.city.strip().lower(), DEFAULT_CITY_COORDS)
        dx, dy = _deterministic_jitter(f'provider:{self.pk}:{self.city}')
        return (base_lat + dx, base_lng + dy)

    @property
    def rating_breakdown(self):
        """Returns {5: count, 4: count, ...} for the star-distribution bar chart."""
        counts = {i: 0 for i in range(5, 0, -1)}
        qs = self.reviews.values('rating').annotate(n=Count('id'))
        for row in qs:
            counts[row['rating']] = row['n']
        return counts
