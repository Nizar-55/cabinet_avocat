from django.urls import path
from . import views

app_name = 'rendezvous'

urlpatterns = [
    path('', views.rendezvous_list, name='list'),
    path('demande/', views.rendezvous_request, name='request'),
    path('<int:pk>/', views.rendezvous_detail, name='detail'),
    path('<int:pk>/traiter/', views.rendezvous_process, name='process'),
    path('<int:pk>/accepter-date/', views.rendezvous_accept_date, name='accept_date'),
    path('<int:pk>/modifier/', views.rendezvous_update, name='update'),
    path('<int:pk>/supprimer/', views.rendezvous_delete, name='delete'),
    path('<int:pk>/confirmer/', views.rendezvous_confirm, name='confirm'),
    path('<int:pk>/annuler/', views.rendezvous_cancel, name='cancel'),
    path('nouveau/', views.rendezvous_create, name='create'),
]