from django.urls import path
from . import views

app_name = 'utilisateurs'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inscription/', views.register_client, name='register'),
    path('profil/', views.profile_view, name='profile'),
    path('profil/password/', views.password_change_view, name='password_change'),
    path('nouveau/', views.create_utilisateur, name='create'),
    path('<int:pk>/', views.utilisateur_detail, name='detail'),
    path('<int:pk>/modifier/', views.utilisateur_update, name='update'),
    path('<int:pk>/avocat/profil/', views.create_avocat_profile, name='create_avocat_profile'),
    path('<int:pk>/secretaire/profil/', views.create_secretaire_profile, name='create_secretaire_profile'),
] 