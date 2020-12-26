from django.urls import path
from .views import MasterKeyList, MasterKeyDetail, KeyUpdate, KeyDelete, KeyDetail

urlpatterns = [
    path('master/<int:pk>/', MasterKeyDetail.as_view()),
    path('master/', MasterKeyList.as_view()),
    path('<int:pk>/', KeyDetail.as_view()),
    path('update/<int:pk>/', KeyUpdate.as_view()),
    path('delete/<int:pk>/', KeyDelete.as_view()),
]
