from django.urls import path
from .views import LockMessageListCreate, LockCatalogList, LockMessageRetrieveDeleteView

urlpatterns = [
    path('lock-catalog/', LockCatalogList.as_view())
]