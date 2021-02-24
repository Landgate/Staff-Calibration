from django.urls import path
from . import views


app_name = 'staffs'

urlpatterns = [
    # path('', views.index, name='home-page'),
    path('', views.staff_list, name = 'staff-list'),
    path('stafftype/', views.stafftype_list, name = 'stafftype-list'),
    path('levels/', views.level_list, name = 'level-list'),
    path('stafftype_create/', views.stafftype_create, name = 'stafftype-create'),
    path('staff_create/', views.staff_create, name = 'staff-create'),
    path('levels/create/', views.level_create, name = 'level-create'),
    path('stafftype/<id>/', views.stafftype_detail, name = 'stafftype-detail'),
    path('levels/<id>/delete', views.level_delete, name = 'level-delete'),
    path('levels/<id>/', views.level_detail, name = 'level-detail'),
    path('stafftype/<id>/delete', views.stafftype_delete, name = 'stafftype-delete'),
    path('stafftype/<id>/update', views.stafftype_update, name = 'stafftype-update'),
    path('levels/<id>/update', views.level_update, name = 'level-update'),
    # path('<id>/', views.staff_detail, name = 'staff-detail'),
    path('<id>/update', views.staff_update, name = 'staff-update'),
    path('<id>/delete', views.staff_delete, name = 'staff-delete'),
]

