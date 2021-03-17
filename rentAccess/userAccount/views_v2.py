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
from .models import Document, UserImage, BillingAddress, PlanRequests, ClientPlan, PlannedClient
from .serializers import (ChangePasswordSerializer,
                          FileUploadSerializer,
                          ProfileUpdateSerializer, ProfileDetailSerializer, UserPlanRequestCreateSerializer,
                          UserPlanSerializer)
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


class ProfileDetailViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):

	@action(detail=True, methods=['get'])
	def retrieve(self, request):
		profile = get_object_or_404(User, id=self.request.user.id)
		serializer = ProfileDetailSerializer(profile, context={'request': request})
		return Response(serializer.data)

	def get_object(self):
		return get_object_or_404(User, id=self.request.user.id)

	@action(detail=True, methods=['put'])
	def change_plan_pro(self, request):
		instance = User.objects.get(id=self.request.user.id)
		request_plan = PlanRequests.objects.get_or_create(
			requested_plan=ClientPlan.objects.get(code='PRO'),
			client=instance
		)

		serializer = UserPlanRequestCreateSerializer(
			request_plan[0],
			context={'request': request}
		)

		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['delete'])
	def reset_plan(self, request):
		instance = User.objects.get(id=self.request.user.id)
		plan = PlannedClient(
			client=instance,
			plan_id='DEFAULT'
		)
		plan.save()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['put'])
	def change_plan_corp(self, request):
		instance = User.objects.get(id=self.request.user.id)
		request_plan = PlanRequests.objects.update_or_create(
			requested_plan=ClientPlan.objects.get(code='CORP'),
			client=instance
		)

		serializer = UserPlanRequestCreateSerializer(
			request_plan[0],
			context={'request': request}
		)

		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def get_plan_request(self, request):
		instance = User.objects.get(id=self.request.user.id)
		request_plan = PlannedClient.objects.all().filter(
			client=instance
		).last()

		serializer = UserPlanSerializer(
			request_plan,
			context={'request': request}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def get_plan_pro_request(self, request):
		instance = User.objects.get(id=self.request.user.id)
		try:
			request_plan = PlanRequests.objects.all().filter(
				client=instance,
				requested_plan=ClientPlan.objects.get(code='PRO'),
			).last()

		except PlanRequests.DoesNotExist:
			request_plan = None
		if not request_plan:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = UserPlanRequestCreateSerializer(
			request_plan,
			context={'request': request}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def get_plan_corp_request(self, request):
		instance = User.objects.get(id=self.request.user.id)
		try:
			request_plan = PlanRequests.objects.all().filter(
				client=instance,
				requested_plan=ClientPlan.objects.get(code='CORP'),
			).last()
		except PlanRequests.DoesNotExist:
			request_plan = None
		if not request_plan:
			return Response(status=status.HTTP_404_NOT_FOUND)
		serializer = UserPlanRequestCreateSerializer(
			request_plan,
			context={'request': request}
		)
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['put'])
	def update(self, request):
		instance = User.objects.get(id=self.request.user.id)
		serializer = ProfileUpdateSerializer(
			instance,
			data=self.request.data,
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

	def get_serializer_class(self):
		if self.action in [
			'change_plan_pro',
			'change_plan_corp',
			'get_plan_request'
		]:
			return UserPlanRequestCreateSerializer
		return ProfileUpdateSerializer


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
		try:
			UserImage.objects.get(account=self.request.user).delete()
		except UserImage.DoesNotExist:
			return Response(status=status.HTTP_404_NOT_FOUND)
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_permissions(self):
		permission_classes = [IsOwnerOrSuperuser, ]
		return [permission() for permission in permission_classes]
