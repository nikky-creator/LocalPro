import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payment(models.Model):
    """
    Records payment for a completed booking.

    NOTE: this is a self-contained SIMULATED payment flow for demo purposes —
    there is no external gateway call. Card details entered at checkout are
    used only for on-screen realism and are never persisted anywhere (not even
    here) — a real integration would replace `payments.views.checkout` with a
    call to a provider's hosted checkout (Razorpay/Stripe/PayU) and would
    never let raw card data touch this server at all.
    """
    METHOD_CARD = 'card'
    METHOD_UPI = 'upi'
    METHOD_NETBANKING = 'netbanking'
    METHOD_CHOICES = [
        (METHOD_CARD, _('Credit / Debit Card')),
        (METHOD_UPI, _('UPI')),
        (METHOD_NETBANKING, _('Net Banking')),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, _('Pending')),
        (STATUS_SUCCESS, _('Success')),
        (STATUS_FAILED, _('Failed')),
    ]

    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='payment')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_CARD)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    transaction_id = models.CharField(max_length=40, unique=True, blank=True, editable=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.transaction_id or "PENDING"} — ₹{self.amount} ({self.status})'

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = 'LP' + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)
