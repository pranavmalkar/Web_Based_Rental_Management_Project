from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('<int:pk>/', views.property_detail, name='property_detail'),

    # owner CRUD
    path('owner/', views.owner_property_list, name='owner_property_list'),
    path('owner/create/', views.property_create, name='property_create'),
    path('owner/<int:pk>/edit/', views.property_update, name='property_update'),
    path('owner/<int:pk>/delete/', views.property_delete, name='property_delete'),
]
