from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated

from .models import Property
from .serializers import PropertySerializer
from .permissions import IsAuthor


class PropertyList(generics.ListCreateAPIView):

	permission_classes = (IsAuthor, )
	queryset = Property.objects.all()
	serializer_class = PropertySerializer

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)

	def get_queryset(self, *args, **kwargs):
		if self.request.user.is_staff or self.request.user.is_superuser:
			return Property.objects.all()
		else:
			return Property.objects.all().filter(author=self.request.user)


class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = (IsAuthor, )
	queryset = Property.objects.filter()
	serializer_class = PropertySerializer
