from django.urls import path
from . import views
from .views import delete_dossiers

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('nouveau/', views.client_create, name='create'),
    path('<int:pk>/', views.client_detail, name='detail'),
    path('<int:pk>/modifier/', views.client_update, name='update'),
    path('<int:pk>/supprimer/', views.client_delete, name='delete'),
    path('<int:pk>/supprimer_dossiers/', delete_dossiers, name='delete_dossiers'),
]