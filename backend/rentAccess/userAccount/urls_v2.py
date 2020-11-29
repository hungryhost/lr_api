from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from properties.views import (
    PropertyList,
    PropertyDetail,
    PropertyCreate,
    PropertyUpdate,
    PropertyDelete
)
from .views_v2 import ProfileDetailViewSet, ProfileDocumentsViewSet, ProfileImageViewSet

from .views import (
    ProfileDetail,
    ProfileList,
    # ChangePasswordView,
   # ProfileUpdate,
    #ProfileDelete,
    ProfileUploadUserPic
)



"""
urlpatterns = [
    path('<int:pk>/', ProfileDetail.as_view(), name='profile_detail'),
    path('test/', ProfileDetailsView.as_view()),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('', ProfileList.as_view()),
    path('<int:pk>/update/', ProfileUpdate.as_view(), name='profile_update'),
    path('<int:pk>/delete/', ProfileDelete.as_view(), name='profile_delete'),
    # TODO: consider using endpoints below:
    # path('<int:pk>/properties/<property_pk>/', PropertyDetail.as_view()),
    # path('<int:pk>/properties/', PropertyList.as_view()),
    # path('<int:pk>/properties/create/', PropertyCreate.as_view()),
    # path('<int:pk>/properties/update/<property_pk>/', PropertyUpdate.as_view()),
    # path('<int:pk>/properties/delete/<property_pk>/', PropertyDelete.as_view()),
    # TODO: uncomment the paths below after adding the views
    path('<int:pk>/upload_userpic/', ProfileUploadUserPic.as_view()),
    # path('delete_userpic/<int:pk>/', ProfileDeleteUserPic.as_view()),
    # path('reset_password/<int:pk>/', ProfileResetPassword.as_view()),
]
"""
change_password = ProfileDetailViewSet.as_view({'patch': 'change_password'})
documents_list = ProfileDocumentsViewSet.as_view({'get': 'list'})
documents_post = ProfileImageViewSet.as_view({'put': 'update_user_picture'})
urlpatterns = [
    path('', ProfileDetailViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'})),
    path('change_password/', change_password),
    path('documents/', ProfileDocumentsViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('userpic/', documents_post),
]

