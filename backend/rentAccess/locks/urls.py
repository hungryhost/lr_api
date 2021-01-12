from django.contrib import admin
from django.urls import path, include
from . import views
from .views import LockDetail


urlpatterns = [
    path('', views.echo),
    # path('<int:lock_id>/', LockDetail.as_view()),
]
