from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.document_list, name='list'),
    path('nouveau/', views.document_create, name='create'),
    path('<str:reference>/', views.document_detail, name='detail'),
    path('<str:reference>/modifier/', views.document_update, name='update'),
    path('<str:reference>/supprimer/', views.document_delete, name='delete'),
    path('<str:reference>/versions/', views.document_versions, name='versions'),
    path('<str:reference>/versions/nouvelle/', views.document_version_create, name='version_create'),
] 