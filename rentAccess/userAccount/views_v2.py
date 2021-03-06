from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bookings.models import Booking
from properties.models import Property
from bookings.serializers import BookingsListSerializer
from properties.serializers import PropertyListSerializer
from .permissions import IsOwnerOrSuperuser
from .models import Document, UserImage, BillingAddress
from .serializers import (ChangePasswordSerializer,
						  FileUploadSerializer,
						  ProfileUpdateSerializer, ProfileDetailSerializer)
from .property_filters import UserPropertyFilter
from .booking_filters import UserBookingsFilter
from django_filters import rest_framework as dj_filters
from rest_framework import filters
from django.db.models import Q

User = get_user_model()


class UserBookingsList(generics.ListAPIView):
	serializer_class = BookingsListSerializer

	filter_backends = (
		dj_filters.DjangoFilterBackend,
		filters.SearchFilter,
		filters.OrderingFilter,)

	filterset_class = UserBookingsFilter

	ordering_fields = [
		'price',
		'created_at',
		'updated_at',
		'status'
	]
	ordering = ['-created_at']
	search_fields = [
		'booked_property__property_address__city__name',
		'booked_property__property_address__street',
		'booked_property__title']

	def get_queryset(self, *args, **kwargs):
		queryset = Booking.objects.prefetch_related(
			'booked_property', 'booked_property__property_address',
			'booked_property__property_address__city',
			'booked_property__property_images'
		).all().filter(client_email=self.request.user.email)
		return queryset

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class UserPropertiesList(generics.ListAPIView):
	serializer_class = PropertyListSerializer
	filter_backends = (
		dj_filters.DjangoFilterBackend,
		filters.SearchFilter,
		filters.OrderingFilter,)
	filterset_class = UserPropertyFilter
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

	def get_queryset(self, *args, **kwargs):
		query = Q()
		query.add(Q(owners__user=self.request.user), query.connector)
		properties = Property.objects.all().select_related(
			'availability', 'property_address', 'property_address__city', 'property_type')
		queryset = properties.filter(
			query
		).prefetch_related('property_images')
		return queryset

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class ProfileDetailViewSet(viewsets.ViewSet):

	def retrieve(self, request):
		profile = get_object_or_404(User, id=self.request.user.id)
		serializer = ProfileDetailSerializer(profile, context={'request': request})
		return Response(serializer.data)

	def get_object(self):
		return get_object_or_404(User, id=self.request.user.id)

	def partial_update(self, request):
		instance = User.objects.get(id=self.request.user.id)
		serializer = ProfileUpdateSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'], url_path='change-password', url_name='change_password')
	def change_password(self, request, *args, **kwargs):
		instance = User.objects.get(id=self.request.user.id)
		serializer = ChangePasswordSerializer(
			instance,
			data=self.request.data,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get_permissions(self):
		permission_classes = [IsOwnerOrSuperuser]
		return [permission() for permission in permission_classes]


class ProfileImageViewSet(viewsets.ViewSet):
	parser_classes = (FormParser, MultiPartParser)

	@action(detail=True, methods=['put'])
	def update_user_picture(self, request):
		serializer = FileUploadSerializer(
			data=self.request.data,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def delete_user_picture(self, request):
		UserImage.objects.get(account=self.request.user).delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_permissions(self):
		permission_classes = [IsOwnerOrSuperuser, ]
		return [permission() for permission in permission_classes]
