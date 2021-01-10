import datetime

from .property_permissions import IsPublicProperty, PropertyOwner300, PropertyOwner400
from .logger_helpers import get_client_ip
from register.models import Key, Lock
from django.db.models import Q
from django.http import Http404
import logging
from rest_framework import generics, permissions, status, response, serializers, viewsets, mixins, exceptions
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Property, Profile, Ownership, PremisesImages, Bookings, LocksWithProperties
from .serializers import PropertySerializer, PropertyUpdateSerializer, \
	PropertyCreateSerializer, PropertyOwnershipListSerializer, PropertyListSerializer, BulkFileUploadSerializer, \
	BookingsListSerializer, BookingsSerializer, BookingUpdateAdminAndCreatorSerializer, \
	BookingUpdateAdminNotCreatorSerializer, BookingUpdateClientSerializer, PropertyOwnershipAddSerializer, \
	PropertyOwnershipUpdateSerializer, BookingCreateFromClientSerializer
from .permissions import IsOwner, IsInitialOwner, BookingIsAdminOfPropertyOrSuperuser, IsOwnerLevel100, \
	IsOwnerLevel200, IsOwnerLevel300, IsOwnerLevel400, IsClientOfBooking, IsSuperUser
from .models import PropertyLog
from locks.serializers import AddLockToPropertySerializer, LockSerializer, LockAndPropertySerializer

crud_logger_info = logging.getLogger('rentAccess.properties.crud.info')
owners_logger = logging.getLogger('rentAccess.properties.owners.info')
bookings_logger = logging.getLogger('rentAccess.properties.bookings.info')
images_logger = logging.getLogger('rentAccess.properties.images.info')


# TODO: owed refactoring: move bookings into their own app
# TODO: fix permissions and requests for owners


class LockList(generics.ListCreateAPIView):
	queryset = Lock.objects.all()

	def create(self, request, *args, **kwargs):
		property_owners = self.get_property_object()
		if not property_owners.objects.filter(premises_id=self.kwargs["pk"],
						user=self.request.user, permission_level_id=400).exists():
			raise exceptions.PermissionDenied
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def get_queryset(self):
		property_owners = self.get_property_object()
		if not property_owners.objects.filter(premises_id=self.kwargs["pk"],
		user=self.request.user, permission_level_id=400).exists() and self.request.method == "GET":
			raise exceptions.PermissionDenied
		return LocksWithProperties.objects.filter(property_id=self.kwargs["pk"])

	def get_serializer_class(self):
		return AddLockToPropertySerializer

	def get_serializer_context(self):
		return {
			'request': self.request,
			'format': self.format_kwarg,
			'view': self,
			'property_id': self.kwargs["pk"]
		}

	def get_property_object(self):
		try:
			property_owners = Property.objects.prefetch_related('owners').get(pk=self.kwargs["pk"])
		except Property.DoesNotExist:
			raise Http404
		return property_owners


class OwnersListCrete(generics.ListCreateAPIView):
	def create(self, request, *args, **kwargs):
		property_owners = self.get_property_object()
		if not property_owners.objects.filter(premises_id=self.kwargs["pk"],
						user=self.request.user, permission_level_id=400).exists():
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

	def get_queryset(self, *args, **kwargs):
		property_owners = self.get_property_object()
		if not property_owners.owners.filter(premises_id=self.kwargs["pk"],
						user=self.request.user).exists() and self.request.method == "GET":
			raise exceptions.PermissionDenied
		return Ownership.objects.all().filter(premises_id=self.kwargs["pk"])

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
	Generic API View class. Lists all objects.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""

	def perform_create(self, serializer):
		obj = serializer.save()
		PropertyLog.objects.create(
			listed_prop=obj,
			user=self.request.user,
			action='POST',
			act_time=datetime.datetime.now(),
			result=True
		)
		Ownership.objects.create(
			premises=obj,
			user=self.request.user,
			is_creator=True,
			permission_level_id=400
		)
		crud_logger_info.info(
			f"object: property; stage: view; action_type: create; user_id: {self.request.user.id}; property_id: {obj.id}; "
			f"ip_addr: {get_client_ip(self.request)}; status: OK;")

	def get_queryset(self, *args, **kwargs):
		return Property.objects.all().filter(visibility=100)

	def get_serializer_class(self):
		if self.request.method == "GET":
			return PropertySerializer
		return PropertyCreateSerializer

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class BookingsListCreateView(generics.ListCreateAPIView):

	def create(self, request, *args, **kwargs):
		property_owners = self.get_property_object()

		if (not property_owners.owners.filter(premises_id=self.kwargs["pk"],
		user=self.request.user, permission_level_id__gte=200).exists()) or (
			property_owners.visibility != 100
		):
			raise exceptions.PermissionDenied
		serializer = self._get_serializer(data=request.data, _property=property_owners)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):
		obj = serializer.save()
		# in here we initialize the key
		bookings_logger.info(
			f"object: booking; stage: view; action_type: create; user_id: {self.request.user.id}; property_id: {self.kwargs['pk']}; "
			f"booking_id: {obj.id}; ip_addr: {self.request.META.get('HTTP_X_FORWARDED_FOR')}; status: OK;")

	def get_queryset(self, *args, **kwargs):
		try:
			property_owners = Property.objects.prefetch_related('owners').get(pk=self.kwargs["pk"])
		except Property.DoesNotExist:
			raise Http404
		if not property_owners.owners.filter(premises_id=self.kwargs["pk"],
						user=self.request.user).exists() and self.request.method == "GET":
			raise exceptions.PermissionDenied
		return Bookings.objects.all().filter(booked_property=self.kwargs["pk"], is_deleted=False)

	def _get_serializer(self, _property, *args, **kwargs):
		"""
		Return the serializer instance that should be used for validating and
		deserializing input, and for serializing output.
		"""
		serializer_class = self._get_serializer_class(_property=_property)
		kwargs.setdefault('context', self.get_serializer_context())
		return serializer_class(*args, **kwargs)

	def get_serializer_context(self):
		return {
			'request': self.request,
			'format': self.format_kwarg,
			'view': self,
			'property_id': self.kwargs["pk"]
		}

	def _get_serializer_class(self, _property):
		if _property.owners.filter(premises_id=self.kwargs["pk"],
			user=self.request.user).exists():
			return BookingsSerializer
		else:
			return BookingCreateFromClientSerializer

	def get_property_object(self):
		try:
			property_owners = Property.objects.prefetch_related('owners').get(pk=self.kwargs["pk"])
		except Property.DoesNotExist:
			raise Http404
		return property_owners


class BookingsAllList(generics.ListAPIView):
	serializer_class = BookingsSerializer

	def get_queryset(self, *args, **kwargs):
		query = Q()
		query.add(Q(booked_property__author=self.request.user) & Q(is_deleted=False), query.connector)
		query.add(Q(booked_property__owners__user=self.request.user) & Q(is_deleted=False), Q.OR)
		return Bookings.objects.filter(
			query
		)

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class BookingsViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	# TODO: instead of deleting a booking -- archive it so that we don't loose any information
	def retrieve(self, request, pk=None, booking_id=None):
		obj = self.get_object(booked_property=pk, booking_id=booking_id)
		serializer = BookingsSerializer(
			obj,
			context={'request': request, 'property_id': pk}
		)
		return Response(serializer.data)

	@action(detail=True, methods=['patch'])
	def partial_update(self, request, pk=None, booking_id=None):
		instance = self.get_object(booked_property=pk, booking_id=booking_id)
		# booked_property = Property.objects.get(id=pk)
		if self.request.user.email == instance.client_email:
			serializer_class = BookingUpdateClientSerializer
		if self.request.user == instance.booked_by:
			serializer_class = BookingUpdateAdminAndCreatorSerializer
		else:
			if instance.booked_property.owners.filter(user=self.request.user).exists():
				serializer_class = BookingUpdateAdminNotCreatorSerializer

		serializer = serializer_class(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request, 'property_id': pk}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()

		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def archive_booking(self, request, pk=None, booking_id=None):
		# instead of deleting a row from db we set is_deleted = True
		# after that a cron job with celery is set to remove the rows with is_deleted = True
		# and transfer it into archive db
		instance = self.get_object(booked_property=pk, booking_id=booking_id)
		instance.is_deleted = True
		instance.save()
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_queryset(self):
		return Bookings.objects.all()

	def get_permissions(self):
		if self.action == 'retrieve':
			permission_classes = [
				IsOwnerLevel100 | IsOwnerLevel200 | IsOwnerLevel300 |
				IsOwnerLevel400 | IsClientOfBooking
			]
		elif self.action == 'partial_update':
			permission_classes = [
			IsOwnerLevel100 | IsOwnerLevel200 | IsOwnerLevel300 |
			IsOwnerLevel400 | IsClientOfBooking
			]
		else:
			permission_classes = [BookingIsAdminOfPropertyOrSuperuser]
		return [permission() for permission in permission_classes]

	def get_object(self, booked_property=None, booking_id=None):
		try:
			obj = Bookings.objects.get(booked_property=booked_property, id=booking_id, is_deleted=False)
			self.check_object_permissions(self.request, obj)
			return obj
		except Bookings.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return BookingsSerializer


class OwnershipViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	r"""
	ViewSet class for CRUD operations with owners of a property.
	"""

	@action(detail=True, methods=['get'])
	def retrieve(self, request, pk=None, owner_id=None):
		obj = self.get_object(pk=pk, owner_id=owner_id)
		serializer = self.get_serializer(
			data=self.request.data,
			context={'request': request, 'property_id': pk}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['patch'])
	def partial_update(self, request, pk=None, owner_id=None):
		instance = self.get_object(pk=pk, owner_id=owner_id)
		serializer = PropertyOwnershipUpdateSerializer(
			instance,
			data=self.request.data,
			partial=True,
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
		permission_classes = [IsInitialOwner]
		return [permission() for permission in permission_classes]

	def get_object(self, pk=None, owner_id=None):
		try:
			obj = Ownership.objects.get(premises=pk, user_id=owner_id)
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

	def retrieve(self, request, pk=None):
		obj = self.get_object(pk=pk)
		serializer = PropertySerializer(
			obj,
			context={'request': request}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['patch'])
	def partial_update(self, request, pk=None):
		instance = self.get_object(pk=pk)
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
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__lte=datetime_start) & Q(booked_until__gte=datetime_start), query_1.connector)
		query_1.add(Q(booked_from__lt=datetime_stop) & Q(booked_until__gte=datetime_stop), Q.OR)
		query_1.add(Q(booked_from__gte=datetime_start) & Q(booked_from__lte=datetime_stop), Q.OR)
		query_1.add(Q(booked_property_id=pk), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=datetime_stop) | Q(booked_until=datetime_start), query_2.connector)
		queryset = Bookings.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			return Response(status=status.HTTP_409_CONFLICT)
		return Response(status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'])
	def change_main_image(self, request, pk=None):
		image_id = self.request.data.get("image_id", None)
		if image_id:
			obj_to_update = get_object_or_404(PremisesImages, pk=image_id)
			obj = PremisesImages.objects.get(premises_id=pk, is_main=True)
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
		if self.action in ['retrieve', 'get_availability']:
			permission_classes = [IsPublicProperty | IsOwner | IsSuperUser]
		if self.action in ['partial_update', 'change_main_image']:
			permission_classes = [PropertyOwner300 | PropertyOwner400 | IsSuperUser]
		if self.action == 'delete_property':
			permission_classes = [PropertyOwner400 | IsSuperUser]
		return [permission() for permission in permission_classes]

	def get_object(self, pk=None, owner_id=None):
		try:
			obj = Property.objects.get(pk=pk)
			self.check_object_permissions(self.request, obj)
			return obj
		except Property.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return PropertySerializer


class PropertyImagesViewSet(viewsets.ViewSet, viewsets.GenericViewSet, mixins.ListModelMixin):

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
				PremisesImages.objects.get(premises_id=pk, pk=item)
			except PremisesImages.DoesNotExist:
				return Response(status=status.HTTP_400_BAD_REQUEST)
		for item in image_ids_list:
			image_obj = get_object_or_404(PremisesImages, pk=item, premises=pk)
			image_obj.delete()
		if not PremisesImages.objects.filter(premises_id=pk, is_main=True).exists() \
				and PremisesImages.objects.filter(premises_id=pk, is_main=False).exists():
			obj = PremisesImages.objects.latest('uploaded_at')
			obj.is_main = True
			obj.save()
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_serializer_class(self):
		if self.action in ['update_property_pictures']:
			return BulkFileUploadSerializer

	def get_permissions(self):
		permission_classes = [IsAuthenticated, ]
		return [permission() for permission in permission_classes]

	def get_parsers(self):
		if self.request.method == "DELETE":
			parser_classes = [JSONParser, ]
		else:
			parser_classes = [FormParser, MultiPartParser]
		return [parser() for parser in parser_classes]
