from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status, exceptions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .documents_serializers import DocumentsSerializer
from .permissions import IsOwnerOrSuperuser
from .models import Document, UserImage
from .serializers import (ChangePasswordSerializer,
						  FileUploadSerializer,
						  ProfileUpdateSerializer, ProfileDetailSerializer)
from .models import CustomUser as User

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
	permission_classes = (IsOwnerOrSuperuser,)
	queryset = Document.objects.all()
	serializer_class = DocumentsSerializer

	def get_queryset(self):
		return Document.objects.all().filter(
			account=self.request.user)


class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
	pass


#class ProfileUpdate(generics.UpdateAPIView):
#	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser)
#	queryset = Profile.objects.all()
#	serializer_class = ProfileUpdateSerializer


#class ProfileDelete(generics.DestroyAPIView):
#	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser,)
#	queryset = Profile.objects.all()
#	serializer_class = ProfileSerializer



