from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from .addresses_views import ProfileAddressesViewSet
from .documents_views import ProfileDocumentsViewSet
from .views_v2 import ProfileDetailViewSet, UserBookingsList, UserPropertiesList, ProfileImageViewSet

app_name = 'userAccount'
change_password = ProfileDetailViewSet.as_view({'put': 'change_password'})
images_post = ProfileImageViewSet.as_view({
    'put': 'update_user_picture',
    'delete': 'delete_user_picture'
    })

router = routers.SimpleRouter()
# router.register(r'', ProfileDocumentsViewSet, basename='documents')
router.register(r'documents', ProfileDocumentsViewSet, basename='documents')


urlpatterns = [
    path('', ProfileDetailViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='user-details'),
    path('change_password/', change_password, name='change-password'),
    path('', include((router.urls, 'userAccount'),)),
    path('billing_addresses/', ProfileAddressesViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('userpic/', images_post, name='userpic'),
    path('bookings/', UserBookingsList.as_view(), name='user-bookings-list'),
    path('properties/', UserPropertiesList.as_view(), name='user-properties-list'),
]
