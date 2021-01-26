from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, exceptions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .documents_serializers import DocumentsSerializer
from .permissions import IsOwnerOrSuperuser, IsCurrentUserOrSuperuser, PersonalInfoAccessList
from .models import Profile, Documents, UserImages
from .serializers import (ProfileSerializer, ChangePasswordSerializer,
						  FileUploadSerializer, ProfileListSerializer,
						  ProfileUpdateSerializer, ProfileDetailSerializer)


# TODO: consider simplifying update/delete/get into one class with ViewSets


class AccountPhonesListCreate(generics.ListCreateAPIView):
	pass


class AccountPhonesDetails(generics.ListCreateAPIView):
	pass


class BillingAddressesDetail(generics.RetrieveUpdateDestroyAPIView):
	pass


class BillingAddressesListCreate(generics.ListCreateAPIView):
	pass


class DocumentsListCreate(generics.ListCreateAPIView):
	permission_classes = (PersonalInfoAccessList,)
	queryset = Documents.objects.all()
	serializer_class = DocumentsSerializer

	def get_queryset(self):
		return Documents.objects.all().filter(
			account=self.request.user)


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
	pass


class ProfileList(generics.ListAPIView):
	throttle_classes = [UserRateThrottle, AnonRateThrottle]
	permission_classes = (permissions.IsAdminUser, )
	queryset = Profile.objects.get_queryset().order_by('user_id')
	serializer_class = ProfileListSerializer


#class ProfileUpdate(generics.UpdateAPIView):
#	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser)
#	queryset = Profile.objects.all()
#	serializer_class = ProfileUpdateSerializer


#class ProfileDelete(generics.DestroyAPIView):
#	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser,)
#	queryset = Profile.objects.all()
#	serializer_class = ProfileSerializer


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Profile.objects.all()

	http_method_names = ['get', 'head']

	def get_serializer_class(self):
		profile = self.get_object()
		if self.request.method == "GET":
			return ProfileDetailSerializer
		if self.request.method == "PATCH":
			return ProfileUpdateSerializer

		return ProfileSerializer

	def destroy(self, request, *args, **kwargs):
		try:
			Profile.objects.get(user=self.request.user).delete()
		except TypeError:
			raise exceptions.NotAuthenticated
		return Response(status=status.HTTP_204_NO_CONTENT)

	def get_permissions(self):
		if self.request.method == 'GET':
			permission_classes = [permissions.IsAuthenticated, ]
		else:
			permission_classes = [permissions.IsAdminUser, ]
		return [permission() for permission in permission_classes]


