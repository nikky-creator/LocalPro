from django.contrib import admin

from .models import ContactMessage, Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'author_role', 'rating', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('author_name', 'quote')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_resolved',)
    readonly_fields = ('created_at',)
