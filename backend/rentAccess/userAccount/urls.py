from django.contrib import admin
from django.urls import path, include
from .views import ProfileDetail, ProfileList

urlpatterns = [
    path('<int:pk>/', ProfileDetail.as_view()),
    path('', ProfileList.as_view())
]
