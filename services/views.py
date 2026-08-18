import math

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProviderProfileForm
from .models import Provider, ServiceCategory


def _haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points, in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(min(1, math.sqrt(a)))


def _parse_user_location(request):
    lat, lng = request.GET.get('lat', '').strip(), request.GET.get('lng', '').strip()
    try:
        return float(lat), float(lng)
    except (TypeError, ValueError):
        return None


def category_list(request):
    categories = ServiceCategory.objects.filter(is_active=True).annotate(
        num_providers=Count('providers', filter=Q(providers__is_available=True))
    ).order_by('order', 'name')
    return render(request, 'services/category_list.html', {'categories': categories})


def provider_list(request):
    providers = Provider.objects.filter(is_available=True).select_related('category', 'user').annotate(
        avg_rating=Avg('reviews__rating'), num_reviews=Count('reviews')
    )

    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()
    city = request.GET.get('city', '').strip()
    min_rating = request.GET.get('rating', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort = request.GET.get('sort', 'recommended').strip()

    if q:
        providers = providers.filter(
            Q(business_name__icontains=q) | Q(bio__icontains=q) | Q(category__name__icontains=q)
            | Q(location__icontains=q) | Q(city__icontains=q)
            | Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
        )
    if category_slug:
        providers = providers.filter(category__slug=category_slug)
    if city:
        providers = providers.filter(city__iexact=city)
    if min_rating:
        try:
            providers = providers.filter(avg_rating__gte=float(min_rating))
        except ValueError:
            pass
    if max_price:
        try:
            providers = providers.filter(price_per_hour__lte=float(max_price))
        except ValueError:
            pass

    sort_map = {
        'rating': '-avg_rating',
        'price_low': 'price_per_hour',
        'price_high': '-price_per_hour',
        'experience': '-experience_years',
    }

    user_location = _parse_user_location(request)

    if sort == 'nearby' and user_location:
        # Distance can't be computed in SQL here (coords may fall back to a
        # per-provider deterministic point), so sort in Python instead.
        user_lat, user_lng = user_location
        providers = list(providers)
        for p in providers:
            p_lat, p_lng = p.map_coords
            p.distance_km = round(_haversine_km(user_lat, user_lng, p_lat, p_lng), 1)
        providers.sort(key=lambda p: p.distance_km)
    else:
        if sort in sort_map:
            providers = providers.order_by(sort_map[sort], '-is_verified')
        else:
            providers = providers.order_by('-is_verified', '-avg_rating', '-num_reviews')
        if user_location:
            user_lat, user_lng = user_location
            providers = list(providers)
            for p in providers:
                p_lat, p_lng = p.map_coords
                p.distance_km = round(_haversine_km(user_lat, user_lng, p_lat, p_lng), 1)

    paginator = Paginator(providers, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'name')
    cities = Provider.objects.values_list('city', flat=True).distinct().order_by('city')

    active_filters = any([q, category_slug, city, min_rating, max_price])

    params = request.GET.copy()
    params.pop('page', None)
    base_qs = params.urlencode()
    if base_qs:
        base_qs += '&'

    map_points = [
        {
            'id': p.pk,
            'name': p.display_name,
            'category': p.category.name,
            'price': float(p.price_per_hour),
            'rating': p.average_rating,
            'lat': p.map_coords[0],
            'lng': p.map_coords[1],
            'distance_km': getattr(p, 'distance_km', None),
            'url': p.get_absolute_url(),
        }
        for p in page_obj.object_list
    ]

    context = {
        'page_obj': page_obj,
        'providers': page_obj.object_list,
        'categories': categories,
        'cities': cities,
        'q': q, 'category_slug': category_slug, 'city': city,
        'min_rating': min_rating, 'max_price': max_price, 'sort': sort,
        'active_filters': active_filters,
        'result_count': paginator.count,
        'base_qs': base_qs,
        'user_location': user_location,
        'map_points': map_points,
    }
    return render(request, 'services/provider_list.html', context)


def provider_detail(request, pk):
    provider = get_object_or_404(
        Provider.objects.select_related('category', 'user'), pk=pk
    )
    reviews = provider.reviews.select_related('customer').order_by('-created_at')
    similar_providers = Provider.objects.filter(
        category=provider.category, is_available=True
    ).exclude(pk=provider.pk).select_related('category')[:4]

    already_booked_pending = False
    if request.user.is_authenticated and getattr(request.user, 'profile', None) and request.user.profile.is_customer:
        already_booked_pending = provider.bookings.filter(
            customer=request.user, status__in=['pending', 'accepted']
        ).exists()

    provider_lat, provider_lng = provider.map_coords

    context = {
        'provider': provider,
        'reviews': reviews,
        'similar_providers': similar_providers,
        'already_booked_pending': already_booked_pending,
        'provider_lat': provider_lat,
        'provider_lng': provider_lng,
    }
    return render(request, 'services/provider_detail.html', context)


@login_required
def provider_profile_edit(request):
    profile = request.user.profile
    if not profile.is_provider:
        messages.error(request, 'Only service provider accounts can manage a listing.')
        return redirect('accounts:dashboard')

    provider = getattr(request.user, 'provider_profile', None)

    if request.method == 'POST':
        form = ProviderProfileForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            provider_obj = form.save(commit=False)
            provider_obj.user = request.user
            provider_obj.save()
            messages.success(request, 'Your service listing is live and up to date!')
            return redirect('accounts:dashboard')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ProviderProfileForm(instance=provider)

    return render(request, 'services/provider_profile_form.html', {'form': form, 'provider': provider})
