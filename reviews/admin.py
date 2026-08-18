from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('provider', 'customer', 'rating', 'short_comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('provider__business_name', 'customer__username', 'comment')
    autocomplete_fields = ('customer', 'provider', 'booking')
    readonly_fields = ('created_at',)

    @admin.display(description='Comment')
    def short_comment(self, obj):
        return (obj.comment[:60] + '…') if len(obj.comment) > 60 else obj.comment
