from django.urls import path

from . import views

app_name = 'services'

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('providers/', views.provider_list, name='provider_list'),
    path('providers/<int:pk>/', views.provider_detail, name='provider_detail'),
    path('provider/listing/', views.provider_profile_edit, name='provider_profile_edit'),
]
