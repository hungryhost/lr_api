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
    # ProfileUpdate,
    # ProfileDelete,
    ProfileUploadUserPic, DocumentsListCreate
)

urlpatterns = [

]
