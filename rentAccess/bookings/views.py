import logging

from django.shortcuts import render
import datetime

from rest_framework.generics import GenericAPIView
from rest_framework.settings import api_settings

from bookings.models import Booking
from django.db.models import Q, Prefetch
from django.http import Http404
from rest_framework import generics, permissions, status, response, serializers, viewsets, mixins, exceptions, \
	decorators
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from register.models import Key
from .permissions import IsOwnerLevel100, IsOwnerLevel200, IsOwnerLevel300, IsOwnerLevel400, \
	IsClientOfBooking, BookingIsAdminOfPropertyOrSuperuser
from rest_framework import generics
from properties.models import LockWithProperty, Property, Ownership
from .serializers import BookingsListSerializer, BookingUpdateAdminAndCreatorSerializer, \
	BookingUpdateAdminNotCreatorSerializer, BookingUpdateClientSerializer, \
	DailyBookingCreateFromClientSerializer, DailyBookingCreateFromOwnerSerializer, \
	HourlyBookingCreateFromClientSerializer, HourlyBookingCreateFromOwnerSerializer

bookings_logger = logging.getLogger('rentAccess.properties.bookings.info')


class BookingsListCreateView(generics.ListCreateAPIView):
	serializer_class = BookingsListSerializer

	def create(self, request, *args, **kwargs):
		user = self.request.user
		try:
			related_property = Property.objects.prefetch_related(
				Prefetch('owners', queryset=Ownership.objects.prefetch_related('user').all())
			).get(pk=self.kwargs['pk'])
		except Property.DoesNotExist:
			raise Http404
		permitted_owners = []
		ownerships = [owner for owner in related_property.owners.all()]
		for owner in ownerships:
			if owner.permission_level_id == 400:
				permitted_owners.append(owner)

		owners = [owner.user for owner in ownerships]
		related_property = Property.objects.select_related(
			'availability',
			'property_address',
			'property_address__city',
			'property_address__city__city').get(pk=self.kwargs['pk'])
		if related_property.visibility != 100 and (not (user in permitted_owners)):
			# if the property is not publicly visible
			# we must check whether the user is an owner and has appropriate permission
			raise exceptions.PermissionDenied
		if user in owners:
			serializer = self._get_serializer(data=request.data, _property=related_property, _owner=True)
			serializer.is_valid(raise_exception=True)
		else:
			serializer = self._get_serializer(data=request.data, _property=related_property, _owner=False)
			serializer.is_valid(raise_exception=True)

		self.perform_create(serializer)

		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def perform_create(self, serializer):
		obj = serializer.save()
		data = {
			"b_id": obj.id,
			"b_start": obj.booked_from,
			"b_end": obj.booked_until,
			"p_id": self.kwargs['pk'],
			"email": obj.client_email,
		}
		try:
			lwp = LockWithProperty.objects.select_related('lock').get(property_id=self.kwargs['pk'])
		except LockWithProperty.DoesNotExist:
			lwp = None
		if lwp:
			key = Key(lock_id=lwp.lock_id, access_start=obj.booked_from, access_stop=obj.booked_until)
			key.save()
			data['key']: key.code
		# send_booking_email_to_client(has_key=True, data=data, duration=0)
		else:
			pass
		# send_booking_email_to_client(has_key=False, data=data, duration=0)

	def get_queryset(self, *args, **kwargs):
		try:
			property_owners = Property.objects.prefetch_related(
				Prefetch('owners', queryset=Ownership.objects.prefetch_related('user').all())).get(pk=self.kwargs['pk'])
		except Property.DoesNotExist:
			raise Http404
		ownerships = [owner.user for owner in property_owners.owners.all()]
		if not (self.request.user in ownerships) and self.request.method == "GET":
			raise exceptions.PermissionDenied
		return Booking.objects.all().filter(booked_property=self.kwargs['pk'], is_deleted=False)

	def _get_serializer(self, _property, _owner=None, *args, **kwargs):
		"""
		Return the serializer instance that should be used for validating and
		deserializing input, and for serializing output.
		"""
		serializer_class = self._get_serializer_class(_property=_property, _owner=_owner)
		kwargs.setdefault('context', self._get_serializer_context(_property=_property))
		return serializer_class(*args, **kwargs)

	def _get_serializer_context(self, _property):
		return {
			'request': self.request,
			'format': self.format_kwarg,
			'view': self,
			'property_id': self.kwargs["pk"],
			'property': _property
		}

	def _get_serializer_class(self, _property, _owner):
		if self.request.method == 'GET':
			return BookingsListSerializer
		else:
			if _owner:
				if _property.booking_type == 100:
					return DailyBookingCreateFromOwnerSerializer
				else:
					return HourlyBookingCreateFromOwnerSerializer
			else:
				if _property.booking_type == 100:
					return DailyBookingCreateFromClientSerializer
				else:
					return HourlyBookingCreateFromClientSerializer


class BookingsAllList(generics.ListAPIView):
	serializer_class = BookingsListSerializer

	def get_queryset(self, *args, **kwargs):
		query = Q()
		query.add(Q(booked_property__owners__user=self.request.user) & Q(is_deleted=False), query.connector)
		return Booking.objects.filter(
			query
		)

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class BookingsViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	# TODO: instead of deleting a booking -- archive it so that we don't loose any information
	def retrieve(self, request, pk=None, booking_id=None):
		obj = self.get_object(booked_property=pk, booking_id=booking_id)
		serializer = BookingsListSerializer(
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
		return Booking.objects.all()

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
			obj = Booking.objects.get(booked_property=booked_property, id=booking_id, is_deleted=False)
			self.check_object_permissions(self.request, obj)
			return obj
		except Booking.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return BookingsListSerializer
