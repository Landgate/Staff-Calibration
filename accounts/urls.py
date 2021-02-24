from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic.base import RedirectView

app_name = 'accounts'
urlpatterns = [
    path('', RedirectView.as_view(url='/', permanent=False), name='accounts_home'),
    path('signup/', views.signup_view, name = 'signup'),
    path('user_list/', views.user_list_view, name = 'user_list'),
    path('sent/', views.activation_sent_view, name = 'activation_sent'),
    path('activate/<slug:uidb64>/<slug:token>/', views.activate_account, name='activate_account'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
    	template_name="registration/password_reset_form.html",
    	email_template_name = "registration/password_reset_email.html",
        success_url = reverse_lazy("accounts:password_reset_done")), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view( template_name="registration/password_reset_done.html"), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view( template_name="registration/password_reset_confirm.html",
        success_url = reverse_lazy("accounts:password_reset_complete")), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view( template_name="registration/password_reset_complete.html"), name='password_reset_complete'),
    path('user_update/<email>/', views.user_update_view, name="user_update"),
    path('user_profile/<id>/', views.user_profile_view, name='user_profile'),
    path('<email>/', views.user_delete, name='user_delete'),
]
