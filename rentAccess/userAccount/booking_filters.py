from django_filters import rest_framework as filters
from bookings.models import Booking


class UserBookingsFilter(filters.FilterSet):
	booked_from_date = filters.DateFilter(field_name='booked_from',
	                                      lookup_expr='date')
	booked_until_date = filters.DateFilter(field_name='booked_until',
	                                      lookup_expr='date')
	created_at_date = filters.DateFilter(field_name='created_at',
	                                       lookup_expr='date')

	class Meta:
		model = Booking
		fields = [
			'status',
			'booked_from_date',
			'booked_until_date'
		]