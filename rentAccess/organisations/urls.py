from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .views import OrganisationsListCreate, OrganisationRetrieveUpdateDeleteView, UserOrganisationMembersListCreateView, \
    PropertyOrganisationMemberListCreateView

app_name = 'organisations'

urlpatterns = [
    path('', OrganisationsListCreate.as_view(), name='organisations'),
    path('<int:pk>/', OrganisationRetrieveUpdateDeleteView.as_view()),
    path('<int:pk>/members/', UserOrganisationMembersListCreateView.as_view(), name='org-members'),
    path('<int:pk>/properties/', PropertyOrganisationMemberListCreateView.as_view(), name='org-properties')
]
