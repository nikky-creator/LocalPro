from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    REASON_NO_SHOW = 'no_show'
    REASON_POOR_QUALITY = 'poor_quality'
    REASON_OVERCHARGED = 'overcharged'
    REASON_UNPROFESSIONAL = 'unprofessional'
    REASON_DAMAGE = 'damage'
    REASON_OTHER = 'other'
    REASON_CHOICES = [
        (REASON_NO_SHOW, _('Provider did not show up')),
        (REASON_POOR_QUALITY, _('Poor quality of work')),
        (REASON_OVERCHARGED, _('Overcharged / price dispute')),
        (REASON_UNPROFESSIONAL, _('Unprofessional behavior')),
        (REASON_DAMAGE, _('Property damage')),
        (REASON_OTHER, _('Other')),
    ]

    STATUS_OPEN = 'open'
    STATUS_REVIEW = 'under_review'
    STATUS_RESOLVED = 'resolved'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_OPEN, _('Open')),
        (STATUS_REVIEW, _('Under Review')),
        (STATUS_RESOLVED, _('Resolved')),
        (STATUS_DISMISSED, _('Dismissed')),
    ]

    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='report')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_filed')
    provider = models.ForeignKey('services.Provider', on_delete=models.CASCADE, related_name='reports_received')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField(max_length=1000)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    admin_notes = models.TextField(blank=True, help_text='Internal notes / resolution details, visible to the reporting customer once resolved.')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Report #{self.pk} — {self.get_reason_display()} ({self.get_status_display()})'

    @property
    def status_color(self):
        return {
            self.STATUS_OPEN: 'gold',
            self.STATUS_REVIEW: 'blue',
            self.STATUS_RESOLVED: 'green',
            self.STATUS_DISMISSED: 'muted',
        }.get(self.status, 'muted')
