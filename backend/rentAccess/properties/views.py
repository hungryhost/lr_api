from datetime import datetime

from django.core.handlers import exception
from rest_framework import generics, permissions, status, response, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Property, Profile
from .serializers import PropertySerializer
from .permissions import IsOwnerOrSuperuser
from .models import PropertyLog


class PropertyList(generics.ListCreateAPIView):
	permission_classes = (IsOwnerOrSuperuser, )
	queryset = Property.objects.all()
	serializer_class = PropertySerializer

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

	def get_queryset(self, *args, **kwargs):
		my_p = Profile.objects.get(user=self.request.user)
		if my_p.user.is_staff or my_p.user.is_superuser:
			return Property.objects.all()
		else:
			return Property.objects.all().filter(author=my_p)


class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = (IsOwnerOrSuperuser, )
	queryset = Property.objects.filter()
	serializer_class = PropertySerializer
