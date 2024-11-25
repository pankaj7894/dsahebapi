from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('name', 'mobile', 'usertype', 'is_active', 'is_staff', 'is_verified')
    list_filter = ('usertype', 'is_active', 'is_staff', 'is_verified')
    search_fields = ('name', 'mobile', 'usertype')
    ordering = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'mobile', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Personal Information', {'fields': ('usertype', 'slug', 'is_verified')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'mobile', 'usertype', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
