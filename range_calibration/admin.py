from django.contrib import admin
from .models import (Calibration_Update, 
                     RawDataModel,
                     AdjustedDataModel,
                     HeightDifferenceModel,
                     RangeParameters,
                     )
# Register your models here.

@admin.register(RangeParameters)
class RangeParamAdmin(admin.ModelAdmin):
    list_display = ('pin','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
    
@admin.register(Calibration_Update)
class CalibrationUpdateAdmin(admin.ModelAdmin):
    list_display = ('observation_date', 'update_index', 'staff_number', 'level_number', 'update_table')
    ordering = ('-observation_date',)

@admin.register(RawDataModel)
class RawDataAdmin(admin.ModelAdmin):
    list_display = ('update_index',
                    'obs_set',
                    'pin',
                    'frm_pin',
                    'to_pin',
                    'observed_ht_diff',
                    'corrected_ht_diff',
                    'standard_deviation')
    ordering = ('-update_index', 'obs_set',)
    
    list_filter = ('observation_date',)
    

@admin.register(AdjustedDataModel)
class AdjustedDataModelAdmin(admin.ModelAdmin):
    list_display = ('observation_date',
                    'pin', 
                    'adjusted_ht_diff',
                    'observed_ht_diff',
                    'residuals',
                    'standard_deviation',
                    'std_dev_residual',
                    'standard_residual')
    ordering = ('-update_index',)

@admin.register(HeightDifferenceModel)
class HeightDifferenceModelAdmin(admin.ModelAdmin):
    list_display = ('observation_date',
                    'pin', 
                    'adjusted_ht_diff',
                    'uncertainty',
                    'observation_count')
    ordering = ('-update_index',)

###########################################################################
# from django.contrib.auth.models import Group, Permission, ContentType
# ## 
# content_type = ContentType.objects.get_for_model(RangeParameters)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(Calibration_Update)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(RawDataModel)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(AdjustedDataModel)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)

# ## 
# content_type = ContentType.objects.get_for_model(HeightDifferenceModel)
# perms = Permission.objects.filter(content_type=content_type)
# group = Group.objects.get(name='Landgate')
# for p in perms:
#     group.permissions.add(p)
