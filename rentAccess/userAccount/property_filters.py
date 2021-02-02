from django_filters import rest_framework as filters
from properties.models import Property


class UserPropertyFilter(filters.FilterSet):
	type = filters.CharFilter(field_name='property_type')
	number_of_clients = filters.NumberFilter(
		field_name='availability__maximum_number_of_clients',
		lookup_expr='gte'
	)
	city = filters.CharFilter(
		field_name='property_address__city',
		lookup_expr='icontains'
	)

	class Meta:
		model = Property
		fields = [
			'number_of_clients',
			'type',
			'city',
			'visibility',
			'active',
			'booking_type',
		]