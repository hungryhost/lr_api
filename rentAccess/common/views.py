from rest_framework import generics, permissions
from properties.models import PropertyType
from .serializers import PropertyTypeListSerializer, CitiesListSerializer
from cities_light.models import City
from .models import SupportedCity


class PropertyTypesListView(generics.ListAPIView):
    queryset = PropertyType.objects.all()
    serializer_class = PropertyTypeListSerializer
    permission_classes = [permissions.IsAuthenticated]


class CitiesListView(generics.ListAPIView):
    serializer_class = CitiesListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SupportedCity.objects.all().select_related('city')
        return queryset
