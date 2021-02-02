from rest_framework import generics, permissions
from properties.models import PropertyTypes
from .serializers import PropertyTypeListSerializer, CitiesListSerializer
from cities_light.models import City
from .models import SupportedCities


class PropertyTypesListView(generics.ListAPIView):
    queryset = PropertyTypes.objects.all()
    serializer_class = PropertyTypeListSerializer
    permission_classes = [permissions.IsAuthenticated]


class CitiesListView(generics.ListAPIView):
    serializer_class = CitiesListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SupportedCities.objects.all().select_related('city')
        return queryset
