import datetime
from django.core.handlers import exception
from django.db.models import Q
from django.http import Http404
from rest_framework import generics, permissions, status, response, serializers, viewsets, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Property, Profile, Ownership, PremisesImages, Bookings
from .serializers import PropertySerializer, PropertyUpdateSerializer, \
	PropertyCreateSerializer, PropertyOwnershipListSerializer, PropertyListSerializer, BulkFileUploadSerializer, \
	BookingsListSerializer, BookingsSerializer, BookingUpdateAdminAndCreatorSerializer, \
	BookingUpdateAdminNotCreatorSerializer, BookingUpdateClientSerializer
from .permissions import IsOwnerOrSuperuser, IsInitialOwner, BookingIsAdminOfPropertyOrSuperuser
from .models import PropertyLog


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
		return Response(status=status.HTTP_201_CREATED)

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
	serializer_class = BookingsSerializer

	def perform_create(self, serializer):
		obj = serializer.save()
		return Response(status=status.HTTP_201_CREATED)

	def get_queryset(self, *args, **kwargs):
		return Bookings.objects.all().filter(booked_property=self.kwargs["pk"])

	def get_serializer_context(self):
		return {
			'request': self.request,
			'format': self.format_kwarg,
			'view': self,
			'property_id': self.kwargs["pk"]
		}

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class BookingsAllList(generics.ListAPIView):
	serializer_class = BookingsSerializer

	def get_queryset(self, *args, **kwargs):
		query = Q(booked_property__author=self.request.user)
		query.add(Q(booked_property__owners__user=self.request.user), Q.OR)
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
		booked_property = Property.objects.get(id=pk)

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
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_queryset(self):
		return Bookings.objects.all()

	def get_permissions(self):
		permission_classes = [BookingIsAdminOfPropertyOrSuperuser]
		return [permission() for permission in permission_classes]

	def get_object(self, booked_property=None, booking_id=None):
		try:
			obj = Bookings.objects.get(booked_property=booked_property, id=booking_id)
			self.check_object_permissions(self.request, obj)
			return obj
		except Bookings.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return BookingsSerializer


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
		endpoint: properties/<property_id>/owners/
			- get list of owners
			- add owner
		endpoint: properties/<property_id>/owners/<user_id>/
			- delete owner
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
		instance = get_object_or_404(Property, author=self.request.user, pk=pk)
		serializer = PropertyUpdateSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def delete_property(self, request, pk=None):
		instance = self.get_object(pk=pk)
		instance.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['get'])
	def list_owners(self, request, pk=None):
		objects = self.get_object().filter(premises=pk).order_by('-is_creator')
		page = self.paginate_queryset(objects)
		if page is not None:
			serializer = PropertyOwnershipListSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		serializer = PropertyOwnershipListSerializer(objects, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def retrieve_owner(self, request, pk=None, owner_id=None):
		obj = self.get_object(pk=pk, owner_id=owner_id)
		serializer = PropertyOwnershipListSerializer(obj)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['post'], permission_classes=[IsInitialOwner])
	def add_owner(self, request, pk=None):
		return Response(status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def destroy_owner(self, request, pk=None, owner_id=None):
		obj = get_object_or_404(Ownership, premises=pk, user_id=owner_id)
		if obj.is_creator:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		obj.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['post'])
	def get_availability(self, request, pk=None):
		"""
		(ArrivalDate <= @ArrivalDate AND DepartureDate >= @ArrivalDate) -- cases 3,5,7
		OR (ArrivalDate < @DepartureDate AND DepartureDate >= @DepartureDate ) --cases 6,6
		OR (@ArrivalDate <= ArrivalDate AND @DepartureDate >= ArrivalDate) --case 4
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
		query_1.add(Q(booked_property_id=1), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=datetime_stop) | Q(booked_until=datetime_start), query_2.connector)
		queryset = Bookings.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			return Response(status=status.HTTP_226_IM_USED)
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
		if self.action in ['retrieve_owner', 'list_owners']:
			return Ownership.objects.all()
		else:
			return Property.objects.all()

	def get_permissions(self):
		if self.action in ['retrieve_owner']:
			permission_classes = [IsInitialOwner]
		else:
			permission_classes = [IsOwnerOrSuperuser]
		return [permission() for permission in permission_classes]

	def get_object(self, pk=None, owner_id=None):
		try:
			if self.action in ['list_owners']:
				return Ownership.objects.all()
			if self.action in ['retrieve_owner']:
				obj = Ownership.objects.get(premises=pk, user_id=owner_id)
				self.check_object_permissions(self.request, obj)
				return obj
		except Ownership.DoesNotExist:
			raise Http404
		try:
			if self.action in ['partial_update', 'retrieve', 'delete_property',
							   'get_availability']:
				obj = Property.objects.get(pk=pk)
				self.check_object_permissions(self.request, obj)
				return obj
		except Property.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		if self.action in ['add_owner', 'retrieve_owner']:
			return PropertyOwnershipListSerializer
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
		permission_classes = [IsOwnerOrSuperuser, ]
		return [permission() for permission in permission_classes]

	def get_parsers(self):
		if self.request.method == "DELETE":
			parser_classes = [JSONParser, ]
		else:
			parser_classes = [FormParser, MultiPartParser]
		return [parser() for parser in parser_classes]
