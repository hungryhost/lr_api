from django.contrib.auth.models import User
from rest_framework import generics, permissions, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsOwnerOrSuperuser, IsCurrentUserOrSuperuser, PersonalInfoAccessList
from .models import Profile, Documents, UserImages
from .serializers import (ProfileSerializer, ChangePasswordSerializer,
						  FileUploadSerializer, ProfileListSerializer,
						  ProfileUpdateSerializer, ProfileDetailSerializer, DocumentsSerializer)


class ProfileDetailViewSet(viewsets.ViewSet):

	def get_queryset(self):
		return Profile.objects.all()

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

	@action(detail=True, methods=['patch'])
	def change_password(self, request, *args, **kwargs):
		instance = User.objects.get(id=self.request.user.id)
		serializer = ChangePasswordSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get_permissions(self):

		if self.request.method.lower() == "list":
			permission_classes = [permissions.AllowAny]
		elif self.request.method.lower() == "update_user_picture":
			permission_classes = [IsCurrentUserOrSuperuser]
		else:
			permission_classes = [IsOwnerOrSuperuser]
		return [permission() for permission in permission_classes]


class ProfileDocumentsViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	def get_queryset(self):
		return Documents.objects.all()

	def list(self, request, *args, **kwargs):
		queryset = Documents.objects.all().filter(account=self.request.user)
		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = DocumentsSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = DocumentsSerializer(queryset, many=True)
		return Response(serializer.data)

	def create(self, request):
		serializer = DocumentsSerializer(
			data=self.request.data,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	def get_serializer_class(self):
		return DocumentsSerializer

	def get_object(self):
		return get_object_or_404(Documents, account=self.request.user)

	def get_permissions(self):
		permission_classes = [PersonalInfoAccessList, ]
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

	def get_permissions(self):
		permission_classes = [PersonalInfoAccessList, ]
		return [permission() for permission in permission_classes]