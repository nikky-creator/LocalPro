from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
    path('receipt/<int:pk>/', views.receipt, name='receipt'),
]
