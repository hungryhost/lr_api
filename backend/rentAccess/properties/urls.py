from django.urls import path
from django.views.generic import TemplateView
from .views import PropertiesViewSet, PropertyListCreate, PropertyImagesViewSet

app_name = 'properties'

properties_details = PropertiesViewSet.as_view({
		'patch': 'partial_update',
		'get': 'retrieve',
		'delete': 'delete_property'
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
	path('<int:pk>/images/', PropertyImagesViewSet.as_view(
		{
			'put': 'update_property_pictures',
			'delete': 'delete_all_images',
		}


	), name='properties-images-list'),
	path('<int:pk>/images/set_main_image/', PropertiesViewSet.as_view(
		{
			'put': 'change_main_image',
		}

	), name='properties-main-image-setter'),
	path('<int:pk>/images/<int:image_id>/', PropertyImagesViewSet.as_view(
		{
			'delete': 'delete_image'
		}
	), name='properties-images-details'),

]
