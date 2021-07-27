from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from .views import GroupListCreateView, UserMembersListCreateView, \
    PropertyGroupMemberListCreateView, GroupRetrieveUpdateDeleteView, bulk_delete_properties, bulk_delete_members

app_name = 'propertyGroups'

urlpatterns = [
    path('', GroupListCreateView.as_view(), name='groups'),
    path('<int:pk>/', GroupRetrieveUpdateDeleteView.as_view()),
    path('<int:pk>/members/', UserMembersListCreateView.as_view(), name='group-members'),
    path('<int:pk>/members/delete/', bulk_delete_members, name='delete-group-members'),
    path('<int:pk>/properties/', PropertyGroupMemberListCreateView.as_view(), name='group-properties'),
    path('<int:pk>/properties/delete/', bulk_delete_properties, name='delete-group-properties'),

]
