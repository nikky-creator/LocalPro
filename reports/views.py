from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from bookings.models import Booking
from .forms import ReportForm
from .models import Report


@login_required
def create_report(request, booking_id):
    booking = get_object_or_404(Booking.objects.select_related('provider'), pk=booking_id)

    if request.user.id != booking.customer_id:
        messages.error(request, "You don't have permission to report that booking.")
        return redirect('bookings:history')
    if booking.status == Booking.STATUS_PENDING:
        messages.error(request, 'You can only report a booking once the provider has responded to it.')
        return redirect('bookings:detail', pk=booking.pk)

    existing = getattr(booking, 'report', None)
    if existing:
        return render(request, 'reports/detail.html', {'report': existing, 'booking': booking})

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.booking = booking
            report.customer = request.user
            report.provider = booking.provider
            report.save()
            messages.success(request, 'Your report has been submitted. Our team will review it shortly.')
            return redirect('bookings:detail', pk=booking.pk)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ReportForm()

    return render(request, 'reports/create.html', {'form': form, 'booking': booking})


@login_required
def my_reports(request):
    reports = Report.objects.filter(customer=request.user).select_related(
        'provider', 'booking'
    ).order_by('-created_at')
    return render(request, 'reports/my_reports.html', {'reports': reports})
