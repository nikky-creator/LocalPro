from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff', 'date_joined')
    list_filter = UserAdmin.list_filter + ('profile__role',)

    @admin.display(description='Role')
    def get_role(self, obj):
        return getattr(obj.profile, 'get_role_display', lambda: '—')()


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city', 'created_at')
    list_filter = ('role', 'city')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    autocomplete_fields = ('user',)


admin.site.site_header = 'LocalPro Administration'
admin.site.site_title = 'LocalPro Admin'
admin.site.index_title = 'Manage the marketplace'
