from django.contrib import admin
from .models import (
    Staff,
    StaffType,
    DigitalLevel,
    #Surveyors
    )
# Register your models here.
@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user','staff_number', 'staff_owner', 'staff_type', 'staff_length','calibration_date')

@admin.register(StaffType)
class StaffTypeAdmin(admin.ModelAdmin):
    list_display = ('staff_type', 'thermal_coefficient')
    ordering = ('staff_type',)

@admin.register(DigitalLevel)
class DigitalLevelAdmin(admin.ModelAdmin):
    list_display = ('user','level_number', 'level_make', 'level_model')
    ordering = ('level_make',)

#admin.site.register(Surveyors)

################################################################
# from django.contrib.auth.models import Group, Permission, ContentType
# ## 
# content_type = ContentType.objects.get_for_model(Staff)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(StaffType)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(DigitalLevel)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

