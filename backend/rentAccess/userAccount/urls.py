from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include


from .views import (
    ProfileDetail,
    ProfileList,
    ChangePasswordView,
    ProfileUpdate,
    ProfileDelete
    )

urlpatterns = [
    path('<int:pk>/', ProfileDetail.as_view()),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),
    path('list/', ProfileList.as_view()),
    path('update/<int:pk>/', ProfileUpdate.as_view()),
    path('delete/<int:pk>/', ProfileDelete.as_view()),
    # TODO: uncomment the paths below after adding the views
    # path('upload_userpic/<int:pk>/', ProfileUploadUserPic.as_view()),
    # path('delete_userpic/<int:pk>/', ProfileDeleteUserPic.as_view()),
    # path('reset_password/<int:pk>/', ProfileResetPassword.as_view()),
]
