from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from .permissions import IsOwnerOfRequest
from .models import LockMessage, LockCatalogInfo
from .serializers import LockMessageCreateSerializer, LockMessageListSerializer, LockInfoSerializer


class LockMessageListCreate(generics.ListCreateAPIView):
	def get_queryset(self, *args, **kwargs):
		return LockMessage.objects.all().prefetch_related(
			'selected_lock',
			'selected_lock__lock_availability',
			'selected_lock__catalog_images',
			'selected_lock__lock_availability__city'
		).filter(email=self.request.user.email)

	def get_serializer_class(self):
		if self.request.method == "GET":
			return LockMessageListSerializer
		return LockMessageCreateSerializer


class LockMessageRetrieveDeleteView(generics.RetrieveDestroyAPIView):
	def get_queryset(self, *args, **kwargs):
		return LockMessage.objects.all()

	def get_serializer_class(self):
		return LockMessageListSerializer
	permission_classes = [IsOwnerOfRequest]


class LockCatalogList(generics.ListAPIView):
	def get_queryset(self, *args, **kwargs):
		return LockCatalogInfo.objects.all().prefetch_related(
			'lock_availability',
			'lock_availability__city',
			'catalog_images').filter(is_available=True)

	def get_serializer_class(self):
		return LockInfoSerializer
