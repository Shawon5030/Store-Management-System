# store/urls.py
from django.urls import path , reverse_lazy
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path("logout/", views.logout_view, name="logout"),
    
    
   path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    

    path('password/change/', auth_views.PasswordChangeView.as_view(
            template_name='auth/password_change.html'
        ), name='password_change'),

    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
            template_name='auth/password_change_done.html'
        ), name='password_change_done'),
    
    
]
