from django.urls import path
from django.views.generic import TemplateView
from .views import PropertiesViewSet, PropertyListCreate

app_name = 'properties'

properties_details = PropertiesViewSet.as_view({
		'patch': 'partial_update',
		'get': 'retrieve'
	})

urlpatterns = [
	path('', PropertyListCreate.as_view(), name='properties-list'),
	path('<int:pk>/owners/<int:owner_id>/', PropertiesViewSet.as_view({
		'get': 'retrieve_owner',
		'delete': 'destroy_owner'
	}), name='owners-details'),
	path('<int:pk>/owners/', PropertiesViewSet.as_view({
		'get': 'list_owners',
		'post': 'add_owner'
	}), name='owners-list'),
	path('<int:pk>/', properties_details, name='properties-details'),
	path('<int:pk>/bookings/', PropertiesViewSet.as_view({
		'post': 'create_booking',
		'get': 'list_bookings'
	}), name='bookings-list'),
]
