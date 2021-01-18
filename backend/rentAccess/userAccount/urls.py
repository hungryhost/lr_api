
from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include

from .views_v2 import AdminAccessUsersViewSet
from .views import ProfileList

app_name = 'adminAccessUserAccounts'
urlpatterns = [
    path('', ProfileList.as_view()),
    path('<int:pk>/', AdminAccessUsersViewSet.as_view({
        'patch': 'change_username',
        'get': 'retrieve',
    }))

]
