from django.urls import path

from . import views

app_name = 'reports'

urlpatterns = [
    path('file/<int:booking_id>/', views.create_report, name='create'),
    path('my-reports/', views.my_reports, name='my_reports'),
]
