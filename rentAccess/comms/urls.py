from django.urls import path
from .views import LockMessageListCreate, LockCatalogList, LockMessageRetrieveDeleteView

urlpatterns = [
    path('lock-requests/', LockMessageListCreate.as_view()),
    path('lock-requests/<int:pk>/', LockMessageRetrieveDeleteView.as_view()),
    path('lock-catalog/', LockCatalogList.as_view())
]