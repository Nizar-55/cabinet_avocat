"""
URL configuration for cabinet project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'cabinet'

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logs/', views.activity_log, name='activity_log'),
    path('admin/alerts/', views.system_alerts, name='system_alerts'),
    path('utilisateurs/', include('utilisateurs.urls')),
    path('clients/', include('clients.urls')),
    path('dossiers/', include('dossiers.urls')),
    path('rendezvous/', include('rendezvous.urls')),
    path('documents/', include('documents.urls')),
    # Style guide for developers (simple static template)
    path('_style_guide/', TemplateView.as_view(template_name="_style_guide.html"), name='style_guide'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
