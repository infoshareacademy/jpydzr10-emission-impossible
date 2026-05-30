from django.urls import path
from . import views

urlpatterns = [
    path('energia/', views.energy_consumption_list, name='energy_consumption_list'),
    path('energia/dodaj/', views.energy_consumption_add, name='energy_consumption_add'),
    path('energia/edytuj/<int:pk>/', views.energy_consumption_edit, name='energy_consumption_edit'),
    path('energia/usun/<int:pk>/', views.energy_consumption_delete, name='energy_consumption_delete'),
    path('energia-zakupiona/', views.energy_purchased_list, name='energy_purchased_list'),
    path('energia-zakupiona/dodaj/', views.energy_purchased_add, name='energy_purchased_add'),
    path('energia-zakupiona/edytuj/<int:pk>/', views.energy_purchased_edit, name='energy_purchased_edit'),
    path('energia-zakupiona/usun/<int:pk>/', views.energy_purchased_delete, name='energy_purchased_delete'),
]