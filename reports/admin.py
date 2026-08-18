from django.contrib import admin

from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'provider', 'customer', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('provider__business_name', 'customer__username', 'description')
    autocomplete_fields = ('customer', 'provider', 'booking')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Report', {'fields': ('booking', 'customer', 'provider', 'reason', 'description')}),
        ('Moderation', {'fields': ('status', 'admin_notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
