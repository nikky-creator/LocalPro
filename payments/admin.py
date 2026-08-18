from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking', 'customer', 'amount', 'method', 'status', 'paid_at')
    list_filter = ('status', 'method')
    search_fields = ('transaction_id', 'customer__username', 'booking__provider__business_name')
    autocomplete_fields = ('customer', 'booking')
    readonly_fields = ('transaction_id', 'created_at')
