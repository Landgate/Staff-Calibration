from django.contrib import admin
from .models import (uCalibrationUpdate, 
                     uRawDataModel,
                     )
# Register your models here.
@admin.register(uCalibrationUpdate)
class uCalibrationUpdateAdmin(admin.ModelAdmin):
    list_display = ('calibration_date', 'update_index', 'staff_number', 'correction_factor', 'correction_factor_temperature')
    ordering = ('-calibration_date',)

@admin.register(uRawDataModel)
class uRawDataAdmin(admin.ModelAdmin):
    list_display = ('update_index',
                    'pin_number',
                    'staff_reading',
                    'number_of_readings',
                    'standard_deviations')
    ordering = ('-calibration_date',)
    
    list_filter = ('calibration_date',)
###########################################################################
# from django.contrib.auth.models import Group, Permission, ContentType
# ## 
# content_type = ContentType.objects.get_for_model(uCalibrationUpdate)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(uRawDataModel)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)