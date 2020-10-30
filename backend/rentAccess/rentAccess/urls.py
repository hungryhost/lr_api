"""rentAccess URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.db import router
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView

from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/property/', include('properties.urls')),
    path('auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('jwtauth.urls'), name='jwtauth'),
    path('api/v1/profile/', include('userAccount.urls')),
    path('api/v1/docs/', TemplateView.as_view(
                      template_name='index.html',
                  ), name='swagger-ui'),
] + static(settings.STATIC_URL)
