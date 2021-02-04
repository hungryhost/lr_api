from rest_framework import serializers, status
from cities_light.models import City
from properties.models import PropertyType
from .models import SupportedCities


class PropertyTypeListSerializer(serializers.ModelSerializer):
	class Meta:
		model = PropertyType
		fields = '__all__'


class CitiesListSerializer(serializers.ModelSerializer):
	locale_name = serializers.CharField(source='city.alternate_names')
	name = serializers.CharField(source='city.name')
	display_name = serializers.CharField(source='city.display_name')
	timezone = serializers.CharField(source='city.timezone')

	class Meta:
		model = SupportedCities
		fields = [
			'name',
			'display_name',
			'locale_name',
			'timezone'
		]