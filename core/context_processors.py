from django.conf import settings


def site_context(request):
    """Makes site branding, footer categories, and role-aware nav badges available everywhere."""
    from services.models import ServiceCategory

    context = {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'LocalPro'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', ''),
        'footer_categories': ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')[:6],
    }

    user = getattr(request, 'user', None)
    if user and user.is_authenticated:
        profile = getattr(user, 'profile', None)
        if profile and profile.role == 'provider' and hasattr(user, 'provider_profile'):
            context['nav_pending_count'] = user.provider_profile.bookings.filter(status='pending').count()
        elif profile and profile.role == 'customer':
            context['nav_active_count'] = user.bookings.filter(status__in=['pending', 'accepted']).count()

    return context
