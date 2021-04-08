from django.urls import path
from django.views.generic import TemplateView
from .views import PropertiesViewSet, PropertyListCreate, PropertyImagesViewSet, \
	LockList, OwnersListCreate, OwnershipViewSet, LocksViewSet
from register.views import CardList, KeyList
from bookings.views import BookingsListCreateView, BookingsViewSet, BookingsAllList
from bookingCalendar.views import AvailabilityExceptionListCreateView

# from .views import LockDetail
app_name = 'properties'

urlpatterns = [
	path('', PropertyListCreate.as_view(), name='properties-list'),
	path('<int:pk>/owners/<int:owner_id>/', OwnershipViewSet.as_view({
		'get'   : 'retrieve',
		'put'   : 'update',
		'delete': 'destroy'
	}), name='properties-owners-details'),

	path('<int:pk>/owners/', OwnersListCreate.as_view(), name='properties-owners-list'),
	path('<int:pk>/', PropertiesViewSet.as_view({
		'patch' : 'partial_update',
		'put'   : 'update',
		'get'   : 'retrieve',
		'delete': 'delete_property'
	}), name='properties-details'),
	path('<int:pk>/favorite/', PropertiesViewSet.as_view({
		'put'   : 'add_to_favorite',
		'delete': 'remove_from_favorite'
	}), name='properties-favorite'),
	path('<int:pk>/bookings/', BookingsListCreateView.as_view(), name='properties-bookings-list'),
	path('<int:pk>/images/', PropertyImagesViewSet.as_view(
		{
			'get'   : 'list',
			'put'   : 'update_property_pictures',
			'delete': 'delete_images',
		}
	), name='properties-images-list'),

	path('<int:pk>/bookings/<int:booking_id>/', BookingsViewSet.as_view(
		{
			'get'   : 'retrieve',
			'put'   : 'update',
			'delete': 'archive_booking'
		}
	), name='properties-bookings-detail'),
	path('<int:pk>/bookings/<int:booking_id>/cancel/', BookingsViewSet.as_view(
		{
			'post': 'cancel_booking'
		}
	), name='properties-bookings-detail-cancel'),
	path('<int:pk>/available/', PropertiesViewSet.as_view({
		'post': 'get_availability',
		'get' : 'get_hourly_availability'
	}), name='properties-availability-check'),
	path('bookings/', BookingsAllList.as_view(), name='properties-bookings-list-all'),
	path('<int:pk>/availability-exceptions/', AvailabilityExceptionListCreateView.as_view(),
	     name='properties-availability-exceptions'),
	path('<int:pk>/images/set_main_image/', PropertiesViewSet.as_view(
		{
			'put': 'change_main_image',
		}

	), name='properties-main-image-setter'),
	path('<int:pk>/locks/', LockList.as_view(), name='properties-locks-list'),
	path('<int:pk>/locks/<int:lock_id>/', LocksViewSet.as_view(
		{
			'get': 'retrieve',
			'put': 'update'
		}
	)),
	path('<int:pk>/locks/<int:lock_id>/accesses/', LocksViewSet.as_view(
		{
			'get': 'get_accesses',
		}
	)),
	path('<int:pk>/locks/<int:lock_id>/cards/', CardList.as_view(), name='properties-cards-list'),
	path('<int:pk>/locks/<int:lock_id>/keys/', KeyList.as_view(), name='properties-keys-list'),
	# path('<int:pk>/images/<int:image_id>/', PropertyImagesViewSet.as_view(
	#	{
	#		'delete': 'delete_image'
	#	}
	# ), name='properties-images-details'),

]
