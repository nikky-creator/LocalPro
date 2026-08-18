from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:provider_id>/', views.create_booking, name='create'),
    path('history/', views.booking_history, name='history'),
    path('<int:pk>/', views.booking_detail, name='detail'),
    path('<int:pk>/cancel/', views.cancel_booking, name='cancel'),
    path('<int:pk>/accept/', views.accept_booking, name='accept'),
    path('<int:pk>/reject/', views.reject_booking, name='reject'),
    path('<int:pk>/complete/', views.complete_booking, name='complete'),
]
