from django.urls import path
from . import views
from .forms import (
        RangeForm1,
        RangeForm2,
    )
app_name = 'range_calibration'

FORMS = [("prefill_form", RangeForm1),
         ("upload_data", RangeForm2),
        ]         

urlpatterns = [
    path('', views.HomeView.as_view(), name='range-home'),
    path('guide', views.guide_view, name='range-guide'),
    path('range_calibrate/', views.RangeCalibrationWizard.as_view(FORMS), name='range-calibrate'),
    path('range_adjust/<update_index>/', views.range_adjust, name='range-adjust'),
    path('range_report/<update_index>/', views.range_report, name='range-report'),
    path('delete_report/<update_index>/', views.delete_report, name='delete-report'),
    path('print_report/<update_index>/', views.print_report, name='print-report'),
    path('range_parameters/',views.range_parameters, name='range-parameters'),
    path('range_param_update/',views.update_range_param, name='range_param_update'),
    
    ]
