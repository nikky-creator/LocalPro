from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from bookings.models import Booking
from .forms import PaymentForm
from .models import Payment


@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('provider', 'provider__category'), pk=booking_id)

    if request.user.id != booking.customer_id:
        messages.error(request, "You don't have permission to pay for that booking.")
        return redirect('accounts:dashboard')
    if booking.status != Booking.STATUS_COMPLETED:
        messages.error(request, 'Payment is available once the service has been marked completed.')
        return redirect('bookings:detail', pk=booking.pk)

    existing = getattr(booking, 'payment', None)
    if existing and existing.status == Payment.STATUS_SUCCESS:
        messages.info(request, 'This booking has already been paid.')
        return redirect('payments:receipt', pk=existing.pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment, _ = Payment.objects.update_or_create(
                booking=booking,
                defaults={
                    'customer': request.user,
                    'amount': booking.estimated_total,
                    'method': form.cleaned_data['method'],
                    'status': Payment.STATUS_SUCCESS,
                    'paid_at': timezone.now(),
                }
            )
            messages.success(request, 'Payment successful! Here is your receipt.')
            return redirect('payments:receipt', pk=payment.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentForm(initial={'method': booking.preferred_payment_method})

    return render(request, 'payments/checkout.html', {'form': form, 'booking': booking})


@login_required
def receipt(request, pk):
    payment = get_object_or_404(
        Payment.objects.select_related('booking', 'booking__provider', 'customer'), pk=pk
    )
    provider = getattr(request.user, 'provider_profile', None)
    is_provider_owner = provider is not None and provider.id == payment.booking.provider_id
    if request.user.id != payment.customer_id and not is_provider_owner:
        messages.error(request, "You don't have permission to view that receipt.")
        return redirect('accounts:dashboard')
    return render(request, 'payments/receipt.html', {'payment': payment})
