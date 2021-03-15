from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import GroupListCreateView, UserMembersListCreateView, \
    PropertyGroupMemberListCreateView, GroupRetrieveUpdateDeleteView

app_name = 'propertyGroups'

urlpatterns = [
    path('', GroupListCreateView.as_view(), name='groups'),
    path('<int:pk>/', GroupRetrieveUpdateDeleteView.as_view()),
    path('<int:pk>/members/', UserMembersListCreateView.as_view(), name='group-members'),
    path('<int:pk>/properties/', PropertyGroupMemberListCreateView.as_view(), name='group-properties')
]
