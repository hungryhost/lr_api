from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from bookings.models import Bookings
from properties.models import Property
from bookings.serializers import BookingsSerializer, BookingsListSerializer
from properties.serializers import PropertyListSerializer
from .permissions import IsOwnerOrSuperuser
from .models import Documents, UserImages, BillingAddresses
from .serializers import (ChangePasswordSerializer,
						  FileUploadSerializer,
						  ProfileUpdateSerializer, ProfileDetailSerializer)

User = get_user_model()


class UserBookingsList(generics.ListAPIView):
	serializer_class = BookingsSerializer

	def get_queryset(self, *args, **kwargs):
		author = get_object_or_404(User, id=self.request.user.id)
		return Bookings.objects.all().filter(client_email=author.email)

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class UserPropertiesList(generics.ListAPIView):
	serializer_class = PropertyListSerializer
	lookup_field = "user_id"

	def get_queryset(self, *args, **kwargs):
		author = get_object_or_404(User, id=self.request.user.id)
		return Property.objects.all().filter(author=author)

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
		UserImages.objects.get(account=self.request.user).delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_permissions(self):
		permission_classes = [IsOwnerOrSuperuser, ]
		return [permission() for permission in permission_classes]
