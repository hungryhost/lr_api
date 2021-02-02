from django.urls import path
from .views import PropertyTypesListView, CitiesListView

urlpatterns = [
	path('property-types/', PropertyTypesListView.as_view(), name='propertytypes-list'),
	path('cities/', CitiesListView.as_view(), name='cities-list'),
]