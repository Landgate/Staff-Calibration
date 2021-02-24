from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Authority

admin.site.site_header = "Landgate Admin"
admin.site.site_title = "Survey Services Portal"
admin.site.index_title = "Welcome to Landgate Staff Range Calibration Portal"

@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ('authority_name', 'authority_abbrev',)

    ordering = ('authority_abbrev',)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'authority', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        #('Personal info', {'fields': ('email', 'phone_number',)}),
        ('Permissions', {'fields': ('is_staff','groups',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 
                'first_name',
                'last_name',
                'authority',
                'password1', 
                'password2',
                'is_staff', 
                'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(CustomUser, CustomUserAdmin)
