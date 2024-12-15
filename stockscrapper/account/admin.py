from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Register your models here.


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name',
                    'phone_no', 'is_active', 'created_at')
    list_filter = ('created_at', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
         'fields': ('first_name', 'last_name', 'phone_no', 'gender')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {
         'fields': ('last_login', 'created_at', 'updated_at')})
    )
    readonly_fields = ('last_login', 'created_at', 'updated_at')
    add_fieldsets = (
        ('Personal Information', {
            'classes': ('extrapretty',),
            'fields': ('email', 'first_name', 'last_name', 'phone_no', 'gender'),
        }),
        ('Permissions', {
            'classes': ('inline',),
            'fields': ('is_staff', 'is_active', 'is_superuser', 'role'),
        }),
        ('Password', {
            'classes': ('wide',),
            'fields': ('password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
