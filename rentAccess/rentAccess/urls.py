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
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenVerifyView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    # ------------------- LOCK-API -------------------
    path('lock-api/v1/echo/', include('locks.urls')),
    path('lock-api/v1/check-access/', include('checkAccess.urls')),
    # integrated into properties
    path('lock-api/v1/register/', include('register.urls')),
    path('lock-api/v1/key/', include('keys.urls')),
    path('lock-api/v1/lock/', include('locks.urls')),
    path('lock-api/v1/access/', include('schedule.urls')),

    # ------------------- SERVICE API -------------------
    path('api/v1/properties/', include('properties.urls'), name='properties'),
    # path('auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('jwtauth.urls'), name='jwtauth'),
    path('api/v1/users/', include('userAccount.urls')),
    path('api/v1/user/', include('userAccount.urls_v2'), name='userAccount'),
    # ------------------- DOCS -------------------
    re_path(r'^watchman/', include('watchman.urls')),
    path('api/v1/service-api-docs/', TemplateView.as_view(
                      template_name='service-api-docs.html',
                  ), name='swagger-ui'),
    path('api/v1/service-specs/general/', TemplateView.as_view(
                      template_name='294_UserAndPropertiesFunctions.html',
                  ), name='workflow'),
    path('api/v1/lock-api-docs/', TemplateView.as_view(
                      template_name='lock-api-docs.html',
                  ), name='swagger-ui'),
] + (
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) +
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)