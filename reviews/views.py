from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from .forms import ReviewForm


@login_required
def add_review(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('provider'), pk=booking_id)

    if request.user.id != booking.customer_id:
        messages.error(request, "You don't have permission to review that booking.")
        return redirect('bookings:history')
    if booking.status != Booking.STATUS_COMPLETED:
        messages.error(request, 'You can only review a booking after the service is completed.')
        return redirect('bookings:detail', pk=booking.pk)
    if hasattr(booking, 'review'):
        messages.info(request, "You've already reviewed this booking.")
        return redirect('bookings:detail', pk=booking.pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.customer = request.user
            review.provider = booking.provider
            review.save()
            messages.success(request, 'Thanks for the review — it helps other customers choose with confidence!')
            return redirect('services:provider_detail', pk=booking.provider_id)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()

    return render(request, 'reviews/add.html', {'form': form, 'booking': booking})
