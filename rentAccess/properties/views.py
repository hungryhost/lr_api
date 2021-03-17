import datetime
import logging

from django.db.models import Q, Prefetch
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django_filters import rest_framework as dj_filters
from rest_framework import filters
from rest_framework import generics, status, viewsets, mixins, exceptions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookings.models import Booking
from locks.serializers import AddLockToPropertySerializer, LockAndPropertySerializer
from .availability_utils import available_days_from_db, available_hours_from_db
from .filters import PropertyFilter
from .logger_helpers import get_client_ip
from .models import Property, Ownership, PremisesImage, LockWithProperty
from .property_permissions import CanBeRetrieved, CanUpdateInfo, CanAddImages, CanDeleteProperty, \
	CanDeleteImages, CanManageOwners, CanDeleteOwners, InOwnership, CanManageLocks, CanDeleteLocks, \
	CanAddLocks
from .serializers import PropertySerializer, PropertyUpdateSerializer, \
	PropertyCreateSerializer, PropertyOwnershipListSerializer, PropertyListSerializer, BulkFileUploadSerializer, \
	PropertyOwnershipAddSerializer, PropertyOwnershipUpdateSerializer, PropertyImagesSerializer
from checkAccess.serializers import AccessListSerializer
from checkAccess.models import AccessLog

crud_logger_info = logging.getLogger('rentAccess.properties.crud.info')
owners_logger = logging.getLogger('rentAccess.properties.owners.info')
images_logger = logging.getLogger('rentAccess.properties.images.info')


class LockList(generics.ListCreateAPIView):

	def create(self, request, *args, **kwargs):
		property_owners = self.get_property_object()
		if not property_owners.owners.filter(
				premises_id=self.kwargs["pk"],
				user=self.request.user,
				permission_level_id=400,
				can_add_locks=True
		).exists():
			raise exceptions.PermissionDenied
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def get(self, request, *args, **kwargs):
		try:
			property_owners = Property.objects.prefetch_related(
				Prefetch(
					'owners',
					queryset=Ownership.objects.select_related('user').all().filter(
						can_manage_locks=True
					))).get(
				pk=self.kwargs['pk'])
		except Property.DoesNotExist:
			raise Http404
		ownerships = [owner.user for owner in property_owners.owners.all()]
		if not (self.request.user in ownerships) and self.request.method == "GET":
			raise exceptions.PermissionDenied
		return super(self.__class__, self).get(self, request, *args, **kwargs)

	def get_queryset(self):
		return LockWithProperty.objects.filter(
			property_id=self.kwargs["pk"])

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return LockAndPropertySerializer
		return AddLockToPropertySerializer

	def get_serializer_context(self):
		return {
			'request'    : self.request,
			'format'     : self.format_kwarg,
			'view'       : self,
			'property_id': self.kwargs["pk"]
		}

	def get_property_object(self):
		try:
			property_owners = Property.objects.prefetch_related('owners').get(pk=self.kwargs["pk"])
		except Property.DoesNotExist:
			raise Http404
		return property_owners


class OwnersListCreate(generics.ListCreateAPIView):
	def create(self, request, *args, **kwargs):
		property_owners = self.get_property_object()
		if not property_owners.owners.filter(
				premises_id=self.kwargs["pk"],
				user=self.request.user,
				permission_level_id=400
		).exists():
			raise exceptions.PermissionDenied
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):
		obj = serializer.save()
		owners_logger.info(
			f"object: owner; stage: view; action_type: create; user_id: {self.request.user.id}; "
			f"owner_id: {obj.id}; property_id: {self.kwargs['pk']} ip_addr: {get_client_ip(self.request)}; status: OK;")

	def get(self, request, *args, **kwargs):
		try:
			property_owners = Property.objects.prefetch_related(
				Prefetch(
					'owners',
					queryset=Ownership.objects.select_related('user').all().filter(
						can_manage_owners=True
					))).get(
				pk=self.kwargs['pk'])
		except Property.DoesNotExist:
			raise Http404
		ownerships = [owner.user for owner in property_owners.owners.all()]
		if not (self.request.user in ownerships) and self.request.method == "GET":
			raise exceptions.PermissionDenied
		return super(self.__class__, self).get(self, request, *args, **kwargs)

	def get_queryset(self, *args, **kwargs):
		return Ownership.objects.all().filter(premises_id=self.kwargs["pk"])

	def get_serializer_context(self):
		return {
			'request'    : self.request,
			'format'     : self.format_kwarg,
			'view'       : self,
			'property_id': self.kwargs["pk"]
		}

	def get_serializer_class(self):
		if self.request.method == "GET":
			return PropertyOwnershipListSerializer
		return PropertyOwnershipAddSerializer

	def get_property_object(self):
		try:
			property_owners = Property.objects.prefetch_related('owners').get(pk=self.kwargs["pk"])
		except Property.DoesNotExist:
			raise Http404
		return property_owners


class PropertyListCreate(generics.ListCreateAPIView):
	"""
	List and create properties.
	"""
	filter_backends = (dj_filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
	filterset_class = PropertyFilter
	ordering_fields = [
		'price',
		'created_at'
	]
	ordering = ['-created_at']
	search_fields = [
		'title',
		'body',
		'property_address__city__name',
		'property_address__street']

	def perform_create(self, serializer):
		obj = serializer.save()
		Ownership.objects.create(
			premises=obj,
			user=self.request.user,
			is_creator=True,
			permission_level_id=400,
			can_edit=True,
			can_delete=True,
			can_add_images=True,
			can_delete_images=True,
			can_add_bookings=True,
			can_manage_bookings=True,
			can_add_owners=True,
			can_manage_owners=True,
			can_delete_owners=True,
			can_add_locks=True,
			can_manage_locks=True,
			can_delete_locks=True,
			can_add_to_group=True,
			can_add_to_organisation=True,
			is_super_owner=True
		),
		crud_logger_info.info(
			f"object: property; stage: view; action_type: create; user_id: {self.request.user.id}; property_id: {obj.id}; "
			f"ip_addr: {get_client_ip(self.request)}; status: OK;")

	def get_queryset(self, *args, **kwargs):
		properties = Property.objects.all().select_related(
			'availability', 'property_address', 'property_address__city', 'property_type')
		queryset = properties.filter(
			~Q(owners__user=self.request.user) & Q(visibility=100)
		).prefetch_related('property_images')
		title = self.request.query_params.get('title', None)
		d_start = self.request.query_params.get('d_start', None)
		d_end = self.request.query_params.get('d_end', None)
		h_start = self.request.query_params.get('h_start', None)
		h_end = self.request.query_params.get('h_end', None)
		booking_type = self.request.query_params.get('booking_type', None)
		try:
			d_start = datetime.datetime.strptime(d_start, "%Y-%m-%d").date()
			d_end = datetime.datetime.strptime(d_end, "%Y-%m-%d").date()

		except Exception:
			d_start = None
			d_end = None
		try:
			h_start = datetime.datetime.strptime(h_start, "%Y-%m-%dT%H:%M")
			h_end = datetime.datetime.strptime(h_end, "%Y-%m-%dT%H:%M")
			h_start = self.request.user.timezone.localize(h_start)
			h_end = self.request.user.timezone.localize(h_end)
		except Exception as e:
			h_start = None
			h_end = None
		if title is not None:
			queryset = queryset.filter(title__icontains=title)
		# due to the complexity of the filtering
		# it is better to handle dates here rather than in the filter backend
		if d_end and d_start and booking_type == '100' and d_start < d_end:
			query_1 = Q()
			query_1.add(
				Q(bookings__booked_from__date__lte=d_start)
				& Q(bookings__booked_until__date__gte=d_start),
				query_1.connector)
			query_1.add(
				Q(bookings__booked_from__date__lt=d_end)
				& Q(bookings__booked_until__date__gte=d_end), Q.OR)
			query_1.add(
				Q(bookings__booked_from__date__gte=d_start)
				& Q(bookings__booked_from__date__lte=d_end), Q.OR)
			query_2 = Q()
			query_2.add(
				Q(bookings__booked_from__date=d_end)
				| Q(bookings__booked_until__date=d_start), Q.AND)

			bad_ids = []
			if queryset.exists():
				for _property in queryset:
					days = available_days_from_db(_property.availability.open_days)
					if not (d_start.weekday() in days) or not (d_end.weekday() in days):
						bad_ids.append(_property.id)
			queryset = queryset.exclude(
				query_1 & ~query_2
			).exclude(Q(id__in=bad_ids))

		if h_start and h_end and booking_type == '200':
			query_1 = Q()
			query_1.add(
				Q(bookings__booked_from__lte=h_start)
				& Q(bookings__booked_until__gte=h_start),
				query_1.connector)
			query_1.add(
				Q(bookings__booked_from__lt=h_end)
				& Q(bookings__booked_until__gte=h_end), Q.OR)
			query_1.add(
				Q(bookings__booked_from__gte=h_start)
				& Q(bookings__booked_from__lte=h_end), Q.OR)
			query_2 = Q()
			query_2.add(
				Q(bookings__booked_from=h_end)
				| Q(bookings__booked_until=h_start), query_2.connector)
			query_3 = Q()
			query_3.add(
				Q(availability__available_from__gt=h_start.time())
				| Q(availability__available_until__lt=h_end.time()),
				query_3.connector)

			bad_ids = []
			if queryset.exists():
				for _property in queryset:
					days = available_days_from_db(_property.availability.open_days)
					if not (h_start.weekday() in days) or not (h_end.weekday() in days):
						bad_ids.append(_property.id)

			queryset = queryset.exclude(
				query_1 & ~query_2
			).exclude(query_3).exclude(Q(id__in=bad_ids))
		return queryset

	def get_serializer_class(self):
		if self.request.method == "GET":
			return PropertyListSerializer
		return PropertyCreateSerializer

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class LocksViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	parser_classes = [JSONParser, ]

	@action(detail=True, methods=['get'])
	def retrieve(self, request, pk=None, lock_id=None):
		try:
			lock = LockWithProperty.objects.get(pk=lock_id, property_id=pk)
		except LockWithProperty.DoesNotExist:
			raise Http404
		serializer = LockAndPropertySerializer(
			lock,
			context={'request': request, 'property_id': pk}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'])
	def update(self, request, pk=None, lock_id=None):
		try:
			lock = LockWithProperty.objects.get(pk=lock_id, property_id=pk)
		except LockWithProperty.DoesNotExist:
			raise Http404
		serializer = AddLockToPropertySerializer(
			lock,
			data=self.request.data,
			partial=False,
			context={'request': request, 'property_id': pk, 'lock_id': lock_id}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def get_accesses(self, request, pk=None, lock_id=None):
		try:
			lock = LockWithProperty.objects.get(pk=lock_id, property_id=pk)
		except LockWithProperty.DoesNotExist:
			raise Http404
		accesses = AccessLog.objects.all().filter(lock=lock.lock.id)
		serializer = AccessListSerializer(
			accesses,
			many=True,
			context={'request': request, 'property_id': pk, 'lock_id': lock_id}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get_queryset(self):
		if self.action in 'get_access':
			return AccessLog.objects.all()

	def get_permissions(self):
		permission_classes = []
		if self.action in ['retrieve', 'get_accesses']:
			permission_classes = [CanManageLocks | CanAddLocks | CanDeleteLocks]
		if self.action == 'update':
			permission_classes = [CanManageLocks]
		if self.action == 'destroy':
			permission_classes = [CanDeleteLocks]
		return [permission() for permission in permission_classes]

	def get_serializer_class(self):
		return AddLockToPropertySerializer


class OwnershipViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	r"""
	ViewSet class for CRUD operations with owners of a property.
	"""
	parser_classes = [JSONParser, ]

	@action(detail=True, methods=['get'])
	def retrieve(self, request, pk=None, owner_id=None):
		obj = self.get_object(pk=pk, owner_id=owner_id)
		serializer = self.get_serializer(
			obj,
			context={'request': request, 'property_id': pk}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'])
	def update(self, request, pk=None, owner_id=None):
		instance = self.get_object(pk=pk, owner_id=owner_id)
		serializer = PropertyOwnershipUpdateSerializer(
			instance,
			data=self.request.data,
			partial=False,
			context={'request': request, 'property_id': pk, 'owner_id': owner_id}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		owners_logger.info(
			f"object: owner; stage: view; action_type: update; user_id: {self.request.user.id}; property_id: {instance.id}; "
			f"owner_id: {instance.id}; ip_addr: {get_client_ip(self.request)}; status: OK;")
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def destroy(self, request, pk=None, owner_id=None):
		instance = self.get_object(pk=pk, owner_id=owner_id)
		instance.delete()
		owners_logger.info(
			f"object: owner; stage: view; action_type: delete; user_id: {self.request.user.id}; property_id: {pk}; "
			f"owner_id: {owner_id}; ip_addr: {get_client_ip(self.request)}; status: OK;")
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_queryset(self):
		return Ownership.objects.all()

	def get_permissions(self):
		permission_classes = []
		if self.action == 'retrieve':
			permission_classes = [InOwnership]
		if self.action == 'update':
			permission_classes = [CanManageOwners]
		if self.action == 'destroy':
			permission_classes = [CanDeleteOwners]
		return [permission() for permission in permission_classes]

	def get_object(self, pk=None, owner_id=None):
		try:
			obj = Ownership.objects.get(premises=pk, pk=owner_id)
			self.check_object_permissions(self.request, obj)
			return obj
		except Ownership.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return PropertyOwnershipListSerializer


class PropertiesViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	r""""
	This viewSet defines the following endpoints:
		endpoint: properties/<property_id>/
			- retrieve (GET) - list a specific property
			- partial_update (PATCH) - partially updates the property
			- destroy (DELETE) - deletes the property
		endpoint: properties/<property_id>/address/
			- partial_update (PATCH) - change address for the property
			- destroy (DELETE) - delete address for the property
		endpoint: properties/<property_id/locks/
			- add lock for the property
			- delete lock for the property
		endpoint: properties/<property_id>/images/
			- upload main and/or additional images
			- delete main and/or additional images

	"""

	@action(detail=True, methods=['get'])
	def retrieve(self, request, pk=None):
		# obj = self.get_object(pk=pk)
		try:
			obj = Property.objects.prefetch_related(
				"property_images",
				"property_address__city",
				"owners",
				"owners__user",
				'mem_groups',
				'mem_groups__group',
				'mem_groups__group__property_groups'
			).select_related(
				'availability',
				'property_type',
				'property_address').get(id=pk)

			self.check_object_permissions(self.request, obj)
		except Property.DoesNotExist:
			raise Http404
		serializer = PropertySerializer(
			obj,
			context={
				'request': request
			}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['patch'])
	def partial_update(self, request, pk=None):
		try:
			instance = Property.objects.prefetch_related(
				"property_images",
				"property_address__city",
				"owners",
				"owners__user",
				'mem_groups',
				'mem_groups__group',
				'mem_groups__group__property_groups'
			).select_related(
				'availability',
				'property_type',
				'property_address').get(id=pk)
			self.check_object_permissions(self.request, instance)
		except Property.DoesNotExist:
			raise Http404
		serializer = PropertyUpdateSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request, "property_id": pk}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		crud_logger_info.info(
			f"object: property; stage: view; action_type: update; user_id: {self.request.user.id}; property_id: {instance.id}; "
			f"ip_addr: {get_client_ip(self.request)}; status: OK;")
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'])
	def update(self, request, pk=None):
		try:
			instance = Property.objects.prefetch_related(
				"property_images",
				"property_address__city",
				"owners",
				"owners__user",
				'mem_groups',
				'mem_groups__group',
				'mem_groups__group__property_groups'
			).select_related(
				'availability',
				'property_type',
				'property_address').get(id=pk)
			self.check_object_permissions(self.request, instance)
		except Property.DoesNotExist:
			raise Http404
		serializer = PropertyUpdateSerializer(
			instance,
			data=self.request.data,
			context={'request': request, "property_id": pk}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		crud_logger_info.info(
			f"object: property; stage: view; action_type: update; user_id: {self.request.user.id}; property_id: {instance.id}; "
			f"ip_addr: {get_client_ip(self.request)}; status: OK;")
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def delete_property(self, request, pk=None):
		instance = self.get_object(pk=pk)
		instance.delete()
		crud_logger_info.info(
			f"object: property; stage: view; action_type: delete; user_id: {self.request.user.id}; property_id: {pk}; "
			f"ip_addr: {get_client_ip(self.request)}; status: OK;")
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['post'])
	def get_availability(self, request, pk=None):
		"""
		(booked_from <= @booked_from AND booked_until >= @booked_from) -- cases 3,5,7
		OR (booked_from < @booked_until AND booked_until >= @DepartureDate ) --cases 6,6
		OR (@booked_from <= booked_from AND @booked_until >= booked_from) --case 4
		"""
		# TODO: consider moving the query into the model's methods or manager
		obj = self.get_object(pk=pk)
		datetime_start = self.request.data.get("booked_from", None)
		datetime_stop = self.request.data.get("booked_until", None)
		number_of_clients = self.request.data.get("number_of_clients", None)
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		try:
			prop = Property.objects.select_related('availability', 'property_type',
			                                       'property_address').get(id=pk)
			self.check_object_permissions(self.request, prop)
		except Property.DoesNotExist:
			raise Http404
		if not datetime_stop or not datetime_start or not number_of_clients:
			return Response(
				status=status.HTTP_400_BAD_REQUEST)

		days = available_days_from_db(prop.availability.open_days)
		if prop.booking_type == 200:
			return Response(data={"No date provided or wrong booking_type of the property"},
			                status=status.HTTP_400_BAD_REQUEST)
		try:
			date_dt_start = datetime.datetime.strptime(datetime_start, '%Y-%m-%d')
			date_dt_end = datetime.datetime.strptime(datetime_stop, '%Y-%m-%d')
		except Exception as e:
			return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
		if date_dt_start.weekday() not in days or date_dt_end.weekday() not in days:
			return Response(
				status=status.HTTP_409_CONFLICT)
		if date_dt_start >= date_dt_end:
			return Response(
				status=status.HTTP_409_CONFLICT)
		if number_of_clients > prop.availability.maximum_number_of_clients:
			return Response(
				status=status.HTTP_409_CONFLICT)
		query_1.add(
			Q(booked_from__lte=datetime_start)
			& Q(booked_until__gte=datetime_start), query_1.connector
		)
		query_1.add(
			Q(booked_from__lt=datetime_stop)
			& Q(booked_until__gte=datetime_stop), Q.OR
		)
		query_1.add(
			Q(booked_from__gte=datetime_start)
			& Q(booked_from__lte=datetime_stop), Q.OR
		)
		query_1.add(
			Q(booked_property_id=pk), Q.AND)
		query_2 = Q()
		query_2.add(
			Q(booked_from=datetime_stop)
			| Q(booked_until=datetime_start), query_2.connector
		)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			return Response(status=status.HTTP_409_CONFLICT)
		return Response(status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def get_hourly_availability(self, request, pk=None):
		try:
			prop = Property.objects.select_related('availability', 'property_type',
			                                       'property_address').get(id=pk)
			self.check_object_permissions(self.request, prop)
		except Property.DoesNotExist:
			raise Http404

		self.check_object_permissions(self.request, prop)

		date = self.request.query_params.get('date', None)
		if (date is None) or prop.booking_type == 100:
			return Response(data={"No date provided or wrong booking_type of the property"},
			                status=status.HTTP_400_BAD_REQUEST)
		try:
			date_dt = datetime.datetime.strptime(date, '%Y-%m-%d')
		except Exception as e:
			return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

		days = available_days_from_db(prop.availability.open_days)
		if date_dt.weekday() not in days:
			return Response(
				data={
					"count"            : 0,
					"property_timezone": prop.property_address.city.city.timezone,
					"available_slots"  : [],
				},
				status=status.HTTP_409_CONFLICT)
		slots = available_hours_from_db(prop, b_date=date_dt)
		data = {
			"count"            : len(slots),
			"property_timezone": prop.property_address.city.city.timezone,
			"available_slots"  : slots,
		}
		# TODO: consider moving the query into the model's methods or manager

		return Response(data=data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'])
	def change_main_image(self, request, pk=None):
		image_id = self.request.data.get("image_id", None)
		if image_id:
			obj_to_update = get_object_or_404(PremisesImage, pk=image_id)
			obj = PremisesImage.objects.get(premises_id=pk, is_main=True)
			obj.is_main = False
			obj.save()
			obj_to_update.set_main()
			obj_to_update.save()
			return Response(status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

	def get_queryset(self):
		return Property.objects.all()

	def get_permissions(self):
		permission_classes = []
		if self.action in ['retrieve', 'get_availability', 'get_hourly_availability']:
			permission_classes = [CanBeRetrieved]
		if self.action in ['partial_update', 'update']:
			permission_classes = [CanUpdateInfo]
		if self.action == 'change_main_image':
			permission_classes = [CanAddImages]
		if self.action == 'delete_property':
			permission_classes = [CanDeleteProperty]
		return [permission() for permission in permission_classes]

	def get_object(self, pk=None, owner_id=None):
		try:
			obj = Property.objects.select_related('availability').get(pk=pk)
			self.check_object_permissions(self.request, obj)
			return obj
		except Property.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return PropertySerializer


class PropertyImagesViewSet(viewsets.ViewSet, viewsets.GenericViewSet, mixins.ListModelMixin):

	def list(self, request, *args, **kwargs):
		try:
			premises = Property.objects.prefetch_related(
				"owners",
				"owners__user").get(
				pk=self.kwargs["pk"]
			)
		except Property.DoesNotExist:
			return Http404
		ownerships = [owner.user for owner in premises.owners.all()]
		if premises.visibility != 100:
			if not (self.request.user in ownerships) and self.request.method == "GET":
				raise exceptions.PermissionDenied

		return super(self.__class__, self).list(self, request, *args, **kwargs)

	@action(detail=True, methods=['put'])
	def update_property_pictures(self, request, pk=None):
		serializer = BulkFileUploadSerializer(
			data=self.request.data,
			context={'request': request, 'premises_id': pk}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(status=status.HTTP_200_OK)

	@action(detail=False, methods=['delete'])
	def delete_images(self, request, pk=None):
		# TODO: redo to use list of items from the query instead of json body
		image_ids_list = list(request.data.get('images'))
		if not all(isinstance(item, int) for item in image_ids_list) or len(image_ids_list) == 0:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		for item in image_ids_list:
			try:
				PremisesImage.objects.get(premises_id=pk, pk=item)
			except PremisesImage.DoesNotExist:
				return Response(status=status.HTTP_400_BAD_REQUEST)
		for item in image_ids_list:
			image_obj = get_object_or_404(PremisesImage, pk=item, premises=pk)
			image_obj.delete()
		if not PremisesImage.objects.filter(premises_id=pk, is_main=True).exists() \
			and PremisesImage.objects.filter(premises_id=pk, is_main=False).exists():
			obj = PremisesImage.objects.latest('uploaded_at')
			obj.is_main = True
			obj.save()
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_serializer_class(self):
		if self.action in ['update_property_pictures']:
			return BulkFileUploadSerializer
		if self.action == 'list':
			return PropertyImagesSerializer

	def get_permissions(self):
		permission_classes = []
		if self.action == "update_property_pictures":
			permission_classes = [CanAddImages, ]
		if self.action == "delete_images":
			permission_classes = [CanDeleteImages, ]
		return [permission() for permission in permission_classes]

	def get_parsers(self):
		if self.request.method in ["DELETE", "GET"]:
			parser_classes = [JSONParser, ]
		else:
			parser_classes = [FormParser, MultiPartParser]
		return [parser() for parser in parser_classes]

	def get_queryset(self):
		if self.action == "list":
			return PremisesImage.objects.all().filter(
				premises=self.kwargs["pk"]
			)
