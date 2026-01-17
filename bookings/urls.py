from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:property_id>/', views.booking_create, name='booking_create'),
    path('traveller/', views.traveller_bookings, name='traveller_bookings'),
    path('owner/', views.owner_bookings, name='owner_bookings'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('<int:pk>/confirm/', views.booking_confirm, name='booking_confirm'),
    path('<int:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
]
