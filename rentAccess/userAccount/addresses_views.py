from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from .permissions import IsOwnerOrSuperuser
from .addresses_serializers import BillingAddressSerializer
from .models import BillingAddresses


class ProfileAddressesViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	def get_queryset(self):
		return BillingAddresses.objects.all()

	def list(self, request, *args, **kwargs):
		queryset = BillingAddresses.objects.all().filter(account=self.request.user)
		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = BillingAddressSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = BillingAddressSerializer(queryset, many=True)
		return Response(serializer.data)

	def create(self, request):
		serializer = BillingAddressSerializer(
			data=self.request.data,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	def partial_update(self, request, pk=None):
		instance = BillingAddresses.objects.get(account=self.request.user, pk=pk)
		serializer = BillingAddressSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get_serializer_class(self):
		return BillingAddressSerializer

	def get_object(self):
		return get_object_or_404(BillingAddresses, account=self.request.user)

	def get_permissions(self):
		permission_classes = [IsOwnerOrSuperuser, ]
		return [permission() for permission in permission_classes]

