from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from .views import homepage
from django.views.static import serve

urlpatterns = [
    path('landgate/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', homepage, name='home'),
    path('docs/', include('docs.urls')),
    # re_path(r'^docs/(?P<path>.*)', serve, {'document_root': settings.DOCS_ROOT}, name='user_guide'),
    path('staffs/', include('staffs.urls')),
    path('range_calibration/', include('range_calibration.urls')),
    path('staff_calibration/', include('staff_calibration.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.UPLOAD_URL, document_root=settings.UPLOAD_ROOT)
# 	urlpatterns += static(settings.DOCS_URL, document_root=settings.DOCS_ROOT)