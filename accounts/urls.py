from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_choice, name='register_choice'),
    path('register/customer/', views.customer_register, name='customer_register'),
    path('register/provider/', views.provider_register, name='provider_register'),
    path('login/', views.LocalProLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
