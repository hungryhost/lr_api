from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include
from properties.views import (
    PropertyList,
    PropertyDetail,
    PropertyCreate,
    PropertyUpdate,
    PropertyDelete
)

from .views import (
    ProfileDetail,
    ProfileList,
    ChangePasswordView,
    ProfileUpdate,
    ProfileDelete, ProfileUploadUserPic
)

urlpatterns = [
    path('<int:pk>/', ProfileDetail.as_view(), name='profile_detail'),
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
