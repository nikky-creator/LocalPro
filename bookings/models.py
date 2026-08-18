from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_ACCEPTED, _('Accepted')),
        (STATUS_REJECTED, _('Rejected')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_CANCELLED, _('Cancelled')),
    ]
    # statuses a customer is still allowed to cancel from
    CANCELLABLE_STATUSES = [STATUS_PENDING, STATUS_ACCEPTED]

    # Kept in sync with payments.Payment.METHOD_CHOICES — this is only the
    # customer's *preference*, captured up front so the provider and the
    # eventual checkout screen both know how the customer intends to pay.
    PAYMENT_CARD = 'card'
    PAYMENT_UPI = 'upi'
    PAYMENT_NETBANKING = 'netbanking'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_CARD, _('Credit / Debit Card')),
        (PAYMENT_UPI, _('UPI')),
        (PAYMENT_NETBANKING, _('Net Banking')),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    provider = models.ForeignKey(
        'services.Provider', on_delete=models.CASCADE, related_name='bookings'
    )
    service_date = models.DateField()
    service_time = models.TimeField()
    address = models.CharField(max_length=255)
    notes = models.TextField(max_length=500, blank=True)
    preferred_payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_UPI,
        help_text='How the customer plans to pay once the job is completed.'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider_note = models.CharField(
        max_length=255, blank=True, help_text='Optional note from provider, e.g. reason for rejection'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.provider.display_name} for {self.customer.username} ({self.status})'

    def get_absolute_url(self):
        return reverse('bookings:detail', args=[self.pk])

    @property
    def is_cancellable(self):
        return self.status in self.CANCELLABLE_STATUSES

    @property
    def is_reviewable(self):
        return self.status == self.STATUS_COMPLETED and not hasattr(self, 'review')

    @property
    def status_color(self):
        return {
            self.STATUS_PENDING: 'gold',
            self.STATUS_ACCEPTED: 'blue',
            self.STATUS_REJECTED: 'danger',
            self.STATUS_COMPLETED: 'green',
            self.STATUS_CANCELLED: 'muted',
        }.get(self.status, 'muted')

    @property
    def estimated_total(self):
        return self.provider.price_per_hour
