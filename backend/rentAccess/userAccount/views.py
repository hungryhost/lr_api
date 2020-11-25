from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrSuperuser, IsCurrentUserOrSuperuser
from .models import Profile
from .serializers import (ProfileSerializer, ChangePasswordSerializer,
						FileUploadSerializer, ProfileListSerializer,
						ProfileUpdateSerializer, ProfileDetailSerializer)


# TODO: add separate classes for POST, GET, PUT, PATCH


class ProfileList(generics.ListAPIView):
	permission_classes = (permissions.IsAdminUser, )
	queryset = Profile.objects.all()
	serializer_class = ProfileListSerializer


class ProfileUpdate(generics.UpdateAPIView):
	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser)
	queryset = Profile.objects.all()
	serializer_class = ProfileUpdateSerializer


class ProfileDelete(generics.DestroyAPIView):
	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser,)
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer


class ProfileDetail(generics.RetrieveAPIView):
	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser,)
	queryset = Profile.objects.all()
	serializer_class = ProfileDetailSerializer


class ChangePasswordView(generics.UpdateAPIView):
	queryset = User.objects.all()
	permission_classes = (IsAuthenticated, IsCurrentUserOrSuperuser,)
	serializer_class = ChangePasswordSerializer


class ProfileUploadUserPic(generics.CreateAPIView):
	# TODO: finish upload class
	parser_classes = (FormParser, MultiPartParser)
	serializer_class = FileUploadSerializer


class ProfileDeleteUserPic(generics.DestroyAPIView):
	pass
