from datetime import datetime
from django.core.handlers import exception
from django.http import Http404
from rest_framework import generics, permissions, status, response, serializers, viewsets, mixins
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Property, Profile, Ownership
from .serializers import PropertySerializer, PropertyUpdateSerializer, \
	PropertyCreateSerializer, PropertyOwnershipListSerializer, PropertyListSerializer
from .permissions import IsOwnerOrSuperuser, IsInitialOwner
from .models import PropertyLog


class PropertyListCreate(generics.ListCreateAPIView):
	"""
	Generic API View class. Lists all objects.
	For owners - lists all of the owner's objects.
	For superusers - lists all objects.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""

	def perform_create(self, serializer):
		obj = serializer.save()
		PropertyLog.objects.create(
			listed_prop=obj,
			user=self.request.user,
			action='POST',
			act_time=datetime.now(),
			result=True
		)
		Ownership.objects.create(
			premises=obj,
			owner=self.request.user,
			is_initial_owner=True,
			permission_level_id=400
		)
		return Response(status=status.HTTP_201_CREATED)

	def get_queryset(self, *args, **kwargs):
		return Property.objects.all().filter(visibility=100)

	def get_serializer_class(self):
		if self.request.method == "GET":
			return PropertyListSerializer
		else:
			return PropertyCreateSerializer

	def get_permissions(self):
		permission_classes = [IsAuthenticated]
		return [permission() for permission in permission_classes]


class PropertiesViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):
	r""""
	This viewSet defines the following endpoints:
		endpoint: properties/<property_id>/
			- retrieve (GET) - list a specific property
			- partial_update (PATCH) - partially updates the property
			- destroy (DELETE) - deletes the property
		endpoint: properties/<property_id>/address/
			- partial_update (PATCH) - change address for the property
			- destroy (DELETE) - delete address for the property
		endpoint: properties/<property_id/locks/
			- add lock for the property
			- delete lock for the property
		endpoint: properties/<property_id>/images/
			- upload main and/or additional images
			- delete main and/or additional images
		endpoint: properties/<property_id>/owners/
			- get list of owners
			- add owner
		endpoint: properties/<property_id>/owners/<user_id>/
			- delete owner
	"""

	def retrieve(self, request, pk=None):
		obj = self.get_object(pk=pk)
		serializer = PropertySerializer(
			obj,
			context={'request': request}
		)
		return Response(serializer.data)

	@action(detail=True, methods=['patch'])
	def partial_update(self, request, pk=None):
		instance = get_object_or_404(Property, author=self.request.user, pk=pk)
		serializer = PropertyUpdateSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	@action(detail=True, methods=['get'])
	def list_owners(self, request, pk=None):
		objects = self.get_object().filter(premises=pk).order_by('-is_initial_owner')
		page = self.paginate_queryset(objects)
		if page is not None:
			serializer = PropertyOwnershipListSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)
		serializer = PropertyOwnershipListSerializer(objects, many=True)
		return Response(serializer.data)

	@action(detail=True, methods=['get'])
	def retrieve_owner(self, request, pk=None, owner_id=None):
		obj = self.get_object(pk=pk, owner_id=owner_id)
		serializer = PropertyOwnershipListSerializer(obj)
		return Response(serializer.data)

	@action(detail=True, methods=['post'], permission_classes=[IsInitialOwner])
	def add_owner(self, request, pk=None):
		pass

	@action(detail=True, methods=['delete'])
	def destroy_owner(self, request, pk=None, owner_id=None):
		obj = get_object_or_404(Ownership, premises=pk, owner=owner_id)
		if obj.is_initial_owner:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		obj.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=['post'], permission_classes=[IsInitialOwner])
	def create_booking(self, request, pk=None):
		obj = get_object_or_404(Ownership, premises=pk, owner=self.request.user)
		if obj.permission_level not in [100, 200, 300, 400]:
			return Response(status=status.HTTP_403_FORBIDDEN)

	def get_queryset(self):
		if self.action in ['retrieve_owner', 'list_owners']:
			return Ownership.objects.all()
		else:
			return Property.objects.all()

	def get_permissions(self):
		if self.action in ['retrieve_owner']:
			permission_classes = [IsInitialOwner]
		else:
			permission_classes = [IsOwnerOrSuperuser]
		return [permission() for permission in permission_classes]

	def get_object(self, pk=None, owner_id=None):
		try:
			if self.action in ['list_owners']:
				return Ownership.objects.all()
			if self.action in ['retrieve_owner']:
				obj = Ownership.objects.get(premises=pk, owner=owner_id)
				self.check_object_permissions(self.request, obj)
				return obj
		except Ownership.DoesNotExist:
			raise Http404
		try:
			if self.action in ['partial_update', 'retrieve']:
				obj = Property.objects.get(pk=pk)
				self.check_object_permissions(self.request, obj)
				return obj
		except Property.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		if self.action in ['add_owner', 'retrieve_owner']:
			return PropertyOwnershipListSerializer
		return PropertySerializer

