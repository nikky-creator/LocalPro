from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.shortcuts import redirect, render

from accounts.models import Profile
from bookings.models import Booking
from reviews.models import Review
from services.models import Provider, ServiceCategory
from .forms import ContactForm
from .models import Testimonial


def home(request):
    categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')[:8]
    featured_providers = (
        Provider.objects.filter(is_available=True)
        .annotate(avg_rating=Avg('reviews__rating'), num_reviews=Count('reviews'))
        .order_by('-is_verified', '-avg_rating', '-num_reviews')[:6]
    )
    testimonials = Testimonial.objects.filter(is_active=True)[:6]

    stats = {
        'providers': Provider.objects.count(),
        'customers': Profile.objects.filter(role=Profile.ROLE_CUSTOMER).count(),
        'completed_bookings': Booking.objects.filter(status=Booking.STATUS_COMPLETED).count(),
        'categories': ServiceCategory.objects.filter(is_active=True).count(),
    }

    context = {
        'categories': categories,
        'featured_providers': featured_providers,
        'testimonials': testimonials,
        'stats': stats,
    }
    return render(request, 'core/home.html', context)


def about(request):
    stats = {
        'providers': Provider.objects.count(),
        'customers': Profile.objects.filter(role=Profile.ROLE_CUSTOMER).count(),
        'completed_bookings': Booking.objects.filter(status=Booking.STATUS_COMPLETED).count(),
        'categories': ServiceCategory.objects.filter(is_active=True).count(),
        'avg_rating': round(Review.objects.aggregate(a=Avg('rating'))['a'] or 0, 1),
    }
    return render(request, 'core/about.html', {'stats': stats})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thanks for reaching out! We'll get back to you within 24 hours.")
            return redirect('core:contact')
        messages.error(request, 'Please correct the errors below and try again.')
    else:
        form = ContactForm()
    return render(request, 'core/contact.html', {'form': form})


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
