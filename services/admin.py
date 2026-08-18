from django.contrib import admin
from django.utils.html import format_html

from .models import Provider, ServiceCategory


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'provider_count', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active', 'color')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        'display_name', 'category', 'city', 'price_per_hour', 'experience_years',
        'star_display', 'is_available', 'is_verified', 'created_at',
    )
    list_filter = ('category', 'city', 'is_available', 'is_verified')
    search_fields = ('business_name', 'user__username', 'user__first_name', 'user__last_name', 'city', 'location')
    autocomplete_fields = ('user',)
    list_editable = ('is_available', 'is_verified')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Account', {'fields': ('user', 'category')}),
        ('Listing details', {'fields': ('business_name', 'bio', 'photo', 'experience_years', 'price_per_hour')}),
        ('Location', {'fields': ('location', 'city')}),
        ('Availability', {'fields': ('is_available', 'availability_days', 'availability_start', 'availability_end')}),
        ('Status', {'fields': ('is_verified', 'created_at', 'updated_at')}),
    )

    @admin.display(description='Rating')
    def star_display(self, obj):
        rating = obj.average_rating
        if not rating:
            return '—'
        return format_html('★ {} ({})', rating, obj.review_count)
