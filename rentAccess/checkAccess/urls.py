from django.urls import path
from .views import check_access_by_card, check_access_by_code


urlpatterns = [
    path('card/', check_access_by_card),
    path('key/', check_access_by_code),
]