from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from bookings.models import Booking
from reviews.models import Review
from .forms import (
    CustomerRegisterForm, ProfileUpdateForm, ProviderRegisterForm, StyledAuthenticationForm,
    UserUpdateForm,
)
from .models import Profile


def register_choice(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/register_choice.html')


def customer_register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! Please log in to continue.')
            return redirect('accounts:login')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomerRegisterForm()
    return render(request, 'accounts/customer_register.html', {'form': form})


def provider_register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = ProviderRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Provider account created! Please log in, then complete your service listing.'
            )
            return redirect('accounts:login')
        messages.error(request, 'Please fix the errors below.')
    else:
        form = ProviderRegisterForm()
    return render(request, 'accounts/provider_register.html', {'form': form})


class LocalProLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        # Used only when no valid ?next= is present; a safe ?next= (e.g. from
        # @login_required on the booking flow) still takes priority over this.
        return str(reverse_lazy('accounts:dashboard'))

    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)
    return render(request, 'accounts/profile.html', {
        'user_form': user_form, 'profile_form': profile_form, 'profile': profile,
    })


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if profile.is_provider:
        provider = getattr(request.user, 'provider_profile', None)
        if provider is None:
            return render(request, 'accounts/provider_dashboard.html', {'provider': None})

        bookings_qs = provider.bookings.select_related('customer').order_by('-created_at')
        from payments.models import Payment
        received = Payment.objects.filter(
            booking__provider=provider, status=Payment.STATUS_SUCCESS
        ).aggregate(total=Sum('amount'))['total'] or 0
        completed_count = bookings_qs.filter(status=Booking.STATUS_COMPLETED).count()
        pending_payout = (provider.price_per_hour * completed_count) - received
        context = {
            'provider': provider,
            'bookings': bookings_qs[:10],
            'pending_count': bookings_qs.filter(status=Booking.STATUS_PENDING).count(),
            'accepted_count': bookings_qs.filter(status=Booking.STATUS_ACCEPTED).count(),
            'completed_count': completed_count,
            'total_bookings': bookings_qs.count(),
            'earnings': received,
            'pending_payout': pending_payout if pending_payout > 0 else 0,
            'recent_reviews': provider.reviews.select_related('customer').order_by('-created_at')[:5],
            'average_rating': provider.average_rating,
        }
        return render(request, 'accounts/provider_dashboard.html', context)

    bookings_qs = Booking.objects.filter(customer=request.user).select_related(
        'provider', 'provider__category'
    ).order_by('-created_at')
    context = {
        'bookings': bookings_qs[:10],
        'pending_count': bookings_qs.filter(status=Booking.STATUS_PENDING).count(),
        'accepted_count': bookings_qs.filter(status=Booking.STATUS_ACCEPTED).count(),
        'completed_count': bookings_qs.filter(status=Booking.STATUS_COMPLETED).count(),
        'total_bookings': bookings_qs.count(),
        'today': timezone.localdate(),
    }
    return render(request, 'accounts/customer_dashboard.html', context)
