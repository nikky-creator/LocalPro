from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from services.models import Provider
from .forms import BookingForm
from .models import Booking


def _redirect_after_provider_action(request, booking):
    if request.POST.get('next') == 'detail':
        return redirect('bookings:detail', pk=booking.pk)
    return redirect('accounts:dashboard')


@login_required
def create_booking(request, provider_id):
    provider = get_object_or_404(Provider.objects.select_related('category', 'user'), pk=provider_id)

    if not request.user.profile.is_customer:
        messages.error(request, 'Only customer accounts can book a service. Please log in as a customer.')
        return redirect('services:provider_detail', pk=provider_id)
    if not provider.is_available:
        messages.error(request, 'This provider is not currently accepting new bookings.')
        return redirect('services:provider_detail', pk=provider_id)
    if provider.user_id == request.user.id:
        messages.error(request, "You can't book your own service listing.")
        return redirect('services:provider_detail', pk=provider_id)

    if request.method == 'POST':
        form = BookingForm(request.POST, provider=provider)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.provider = provider
            booking.save()
            messages.success(
                request,
                f'Your booking request with {provider.display_name} has been sent! '
                f"You'll be notified once they respond."
            )
            return redirect('bookings:detail', pk=booking.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        initial = {}
        profile = getattr(request.user, 'profile', None)
        if profile and profile.address:
            initial['address'] = profile.address
        form = BookingForm(provider=provider, initial=initial)

    return render(request, 'bookings/create.html', {'form': form, 'provider': provider})


@login_required
def booking_history(request):
    profile = request.user.profile
    if profile.is_provider:
        return redirect('accounts:dashboard')

    status_filter = request.GET.get('status', '').strip()
    bookings = Booking.objects.filter(customer=request.user).select_related(
        'provider', 'provider__category'
    ).order_by('-created_at')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    paginator = Paginator(bookings, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)
    base_qs = params.urlencode()
    if base_qs:
        base_qs += '&'

    return render(request, 'bookings/history.html', {
        'page_obj': page_obj,
        'bookings': page_obj.object_list,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
        'result_count': paginator.count,
        'base_qs': base_qs,
    })


def _user_can_view_booking(user, booking):
    is_owner_customer = user.id == booking.customer_id
    provider = getattr(user, 'provider_profile', None)
    is_owner_provider = provider is not None and provider.id == booking.provider_id
    return is_owner_customer or is_owner_provider


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('provider', 'provider__category', 'customer'), pk=pk
    )
    if not _user_can_view_booking(request.user, booking):
        messages.error(request, "You don't have permission to view that booking.")
        return redirect('accounts:dashboard')
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.user.id != booking.customer_id:
        messages.error(request, "You don't have permission to cancel that booking.")
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        if booking.is_cancellable:
            booking.status = Booking.STATUS_CANCELLED
            booking.save()
            messages.success(request, f'Booking #{booking.pk} has been cancelled.')
        else:
            messages.error(request, 'This booking can no longer be cancelled.')
    return redirect('bookings:detail', pk=pk)


@login_required
def accept_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    provider = getattr(request.user, 'provider_profile', None)
    if provider is None or provider.id != booking.provider_id:
        messages.error(request, "You don't have permission to update that booking.")
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        if booking.status == Booking.STATUS_PENDING:
            booking.status = Booking.STATUS_ACCEPTED
            booking.save()
            messages.success(request, f'Booking #{booking.pk} accepted. The customer has been notified.')
        else:
            messages.error(request, 'Only pending bookings can be accepted.')
    return _redirect_after_provider_action(request, booking)


@login_required
def reject_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    provider = getattr(request.user, 'provider_profile', None)
    if provider is None or provider.id != booking.provider_id:
        messages.error(request, "You don't have permission to update that booking.")
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        if booking.status == Booking.STATUS_PENDING:
            booking.status = Booking.STATUS_REJECTED
            booking.provider_note = request.POST.get('reason', '').strip()[:255]
            booking.save()
            messages.info(request, f'Booking #{booking.pk} was rejected.')
        else:
            messages.error(request, 'Only pending bookings can be rejected.')
    return _redirect_after_provider_action(request, booking)


@login_required
def complete_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    provider = getattr(request.user, 'provider_profile', None)
    if provider is None or provider.id != booking.provider_id:
        messages.error(request, "You don't have permission to update that booking.")
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        if booking.status == Booking.STATUS_ACCEPTED:
            booking.status = Booking.STATUS_COMPLETED
            booking.save()
            messages.success(request, f'Booking #{booking.pk} marked as completed. Great work!')
        else:
            messages.error(request, 'Only accepted bookings can be marked as completed.')
    return _redirect_after_provider_action(request, booking)
