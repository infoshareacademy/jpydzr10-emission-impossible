from django.urls import path
from . import views

urlpatterns = [
    path('energia/', views.energy_consumption_list, name='energy_consumption_list'),
    path('energia/dodaj/', views.energy_consumption_add, name='energy_consumption_add'),
    path('energia/edytuj/<int:pk>/', views.energy_consumption_edit, name='energy_consumption_edit'),
    path('energia/usun/<int:pk>/', views.energy_consumption_delete, name='energy_consumption_delete'),
]