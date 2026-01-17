from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/<int:booking_id>/', views.create_payment, name='create_payment'),
    path('payment/<int:payment_id>/', views.payment_page, name='payment_page'),
    path('success/', views.payment_success, name='payment_success'),
    path('failed/', views.payment_failed, name='payment_failed'),
]