from django.contrib import admin
from django.conf.urls import url
from django.urls import path, include


from .views import ProfileDetail, ProfileList, ChangePasswordView

urlpatterns = [
    path('<int:pk>/', ProfileDetail.as_view()),
    path('', ProfileList.as_view()),
    path('change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password')

]
