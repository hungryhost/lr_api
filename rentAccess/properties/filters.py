from django_filters import rest_framework as filters
from .models import Property


class PropertyFilter(filters.FilterSet):
	min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
	max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
	type = filters.CharFilter(field_name='property_type')
	number_of_clients = filters.NumberFilter(
		field_name='availability__maximum_number_of_clients',
		lookup_expr='gte'
	)
	city = filters.CharFilter(
		field_name='property_address__city',
		lookup_expr='icontains'
	)
	street = filters.CharFilter(
		field_name='property_address__street',
		lookup_expr='icontains'
	)

	class Meta:
		model = Property
		fields = [
			'number_of_clients',
			'type',
			'city',
			'street',
			'booking_type',
			'min_price',
			'max_price'
		]
