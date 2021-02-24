from django.urls import path
from . import views

app_name = 'staff_calibration'

urlpatterns = [
    path('', views.homeview, name="staff-home"),
    path('user_staff_lists/', views.user_staff_lists, name="user-staff-lists"),
    path('staff_guide/', views.guideview, name="staff-guide"),
    path('staff_calibrate/', views.calibrate, name="staff-calibrate"),
    path('generate_report/<update_index>/', views.generate_report_view, name='generate-report'),
    path('<update_index>/delete', views.user_staff_delete, name = 'user-staff-delete'),
]

