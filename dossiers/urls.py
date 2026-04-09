from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.dossier_list, name='list'),
    path('nouveau/', views.dossier_create, name='nouveau'),
    path('<str:reference>/', views.dossier_detail, name='detail'),
    path('<str:reference>/modifier/', views.dossier_update, name='update'),
    path('<str:reference>/supprimer/', views.dossier_delete, name='delete'),
] 