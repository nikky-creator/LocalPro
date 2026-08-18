from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'provider', 'service_date', 'service_time', 'status', 'created_at')
    list_filter = ('status', 'service_date', 'provider__category')
    search_fields = ('customer__username', 'provider__business_name', 'provider__user__username', 'address')
    autocomplete_fields = ('customer', 'provider')
    date_hierarchy = 'service_date'
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30
