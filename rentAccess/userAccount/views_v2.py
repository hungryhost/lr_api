from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from properties.models import Bookings, Property
from properties.serializers import BookingsSerializer, PropertyListSerializer, BookingsListSerializer
from .permissions import IsOwnerOrSuperuser, IsCurrentUserOrSuperuser, PersonalInfoAccessList
from .models import Profile, Documents, UserImages, BillingAddresses
from .serializers import (ProfileSerializer, ChangePasswordSerializer,
						  FileUploadSerializer, ProfileListSerializer,
						  ProfileUpdateSerializer, ProfileDetailSerializer)


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
		profile = get_object_or_404(Profile, user=self.request.user)
		serializer = ProfileDetailSerializer(profile, context={'request': request})
		return Response(serializer.data)

	def get_object(self):
		return get_object_or_404(Profile, user=self.request.user)

	def partial_update(self, request):
		instance = Profile.objects.get(user=self.request.user)
		serializer = ProfileUpdateSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['patch'], url_path='change-username', url_name='change_username')
	def change_username(self, request):
		try:
			user = User.objects.get(pk=self.request.user.id)
			username = self.request.data["username"]
			user.username = username
			user.save()
			serializer = ProfileDetailSerializer(instance=Profile.objects.get(user=user))
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(status=status.HTTP_400_BAD_REQUEST)

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


class AdminAccessUsersViewSet(viewsets.ViewSet):

	@action(detail=True, methods=['patch'])
	def change_username(self, request, pk):
		try:
			user = User.objects.get(pk=pk)
			username = self.request.data["username"]
			user.username = username
			user.save()
			serializer = ProfileDetailSerializer(
				instance=Profile.objects.get(user=user),
				context={'request': request}
			)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except Exception as e:
			return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

	def retrieve(self, request, pk=None):
		profile = get_object_or_404(Profile, user=get_object_or_404(User, pk=pk))
		serializer = ProfileDetailSerializer(profile, context={'request': request})
		return Response(serializer.data)

	@action(detail=False, methods=['post'], url_path='suspend-user', url_name='suspend_user')
	def suspend_user(self, request):
		try:
			return Response(status=status.HTTP_200_OK)
		except Exception as e:
			return Response(status=status.HTTP_400_BAD_REQUEST)

	@action(detail=False, methods=['post'], url_path='unsuspend-user', url_name='unsuspend_user')
	def unsuspend_user(self, request):
		try:
			return Response(status=status.HTTP_200_OK)
		except Exception as e:
			return Response(status=status.HTTP_400_BAD_REQUEST)

	def get_queryset(self):
		return Profile.objects.all()

	def get_serializer_class(self):
		return ProfileDetailSerializer

	def get_object(self):
		return get_object_or_404(Profile, user=self.request.user)

	def get_permissions(self):
		permission_classes = [permissions.IsAdminUser, ]
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
		permission_classes = [PersonalInfoAccessList, ]
		return [permission() for permission in permission_classes]