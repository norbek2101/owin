from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for the User model.
    """
    model = User
    list_display = ('name', 'email', 'phone_number', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('name', 'email', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'phone_number', 'password1', 'password2'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    def get_queryset(self, request):
        """
        Optimize queryset to reduce database queries.
        """
        return super().get_queryset(request).prefetch_related('groups', 'groups__permissions', 'user_permissions')

    def save_model(self, request, obj, form, change):
        """
        Ensure password is hashed when creating or updating a user.
        """
        if not change or (change and form.cleaned_data.get('password')):
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)