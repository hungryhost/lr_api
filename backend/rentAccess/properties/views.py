from datetime import datetime

from django.core.handlers import exception
from rest_framework import generics, permissions, status, response, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Property, Profile
from .serializers import PropertySerializer, PropertyCreateUpdateSerializer
from .permissions import IsOwnerOrSuperuser
from .models import PropertyLog


class PropertyList(generics.ListAPIView):
	"""
	Generic API View class. Lists all objects.
	For owners - lists all of the owner's objects.
	For superusers - lists all objects.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	permission_classes = (IsOwnerOrSuperuser, IsAuthenticated,)
	queryset = Property.objects.all()
	serializer_class = PropertySerializer
	"""
	def perform_create(self, serializer):
		my_p = Profile.objects.get(user=self.request.user)
		serializer.save(author=my_p)
		curr_prop = serializer.save(author=my_p)

		PropertyLog.objects.create(
			listed_prop=curr_prop,
			user=self.request.user,
			action='POST',
			act_time=datetime.now(),
			result=True
		)
		return Response(status=status.HTTP_201_CREATED)
	"""

	def get_queryset(self, *args, **kwargs):
		my_p = Profile.objects.get(user=self.request.user)
		if my_p.user.is_staff or my_p.user.is_superuser:
			return Property.objects.all()
		else:
			return Property.objects.all().filter(author=my_p)


class PropertyCreate(generics.CreateAPIView):
	"""
	Generic API View class. Used for creating objects.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	permission_classes = (IsOwnerOrSuperuser, IsAuthenticated)
	queryset = Property.objects.filter()
	serializer_class = PropertyCreateUpdateSerializer


class PropertyUpdate(generics.UpdateAPIView):
	"""
	Generic API View class. Used for updating objects.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser, )
	queryset = Property.objects.filter()
	serializer_class = PropertyCreateUpdateSerializer


class PropertyDetail(generics.RetrieveAPIView):
	"""
		Generic API View class. Used for retrieving details about an object.
		Author: Y. Borodin (gitlab: yuiborodin)
		Version: 1.0
		Last Update: 16.11.2020
	"""
	permission_classes = (IsOwnerOrSuperuser, IsAuthenticated, )
	queryset = Property.objects.filter()
	serializer_class = PropertySerializer


class PropertyDelete(generics.DestroyAPIView):
	"""
	Generic API View class. Used for deleting an object.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	permission_classes = (IsOwnerOrSuperuser, IsAuthenticated,)
	queryset = Property.objects.filter()
	serializer_class = PropertySerializer
