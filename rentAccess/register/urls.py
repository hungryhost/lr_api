from django.urls import path
from .views import LockList, CardList, KeyList


urlpatterns = [
    path('lock/', LockList.as_view()),
    path('card/', CardList.as_view()),
    path('key/', KeyList.as_view()),
]
