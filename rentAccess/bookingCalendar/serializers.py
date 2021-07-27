from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers, status
import logging
import pytz
from properties.models import AvailabilityException, Property
from bookings.custom_validation_errors import CustomValidation


class AvailabilityExceptionSerializer(serializers.ModelSerializer):
	datetime_start = serializers.DateTimeField(
		source='exception_datetime_start',
		required=True,
		allow_null=False
	)
	datetime_end = serializers.DateTimeField(
		source='exception_datetime_end',
		required=True,
		allow_null=False
	)

	class Meta:
		model = AvailabilityException
		fields = [
			'id',
			'datetime_start',
			'datetime_end'
		]

	def validate(self, attrs):
		premises_id = self.context['premises_id']
		try:
			premises = Property.objects.select_related(
				'property_address', 'property_address__city'
			).get(pk=premises_id)
		except Property.DoesNotExist:
			raise CustomValidation(
				status_code=400,
				field='property',
				detail="Property does not exist."
			)
		tz = pytz.timezone(premises.property_address.city.city.timezone)
		datetime_ = tz.localize(datetime.now())

		if attrs["exception_datetime_start"] <= datetime_ or attrs["exception_datetime_end"] <= datetime_:
			raise CustomValidation(
				status_code=400,
				field='dates',
				detail="Cannot create an exception for invalid datetime."
			)
		return super(AvailabilityExceptionSerializer, self).validate(attrs)

	def create(self, validated_data):
		print(validated_data)
		datetime_start = validated_data.get('exception_datetime_start')
		datetime_end = validated_data.get('exception_datetime_end')
		premises_id = self.context['premises_id']
		try:
			premises = Property.objects.get(pk=premises_id)
		except Property.DoesNotExist:
			raise CustomValidation(
				status_code=400,
				field='property',
				detail="Property does not exist."
			)
		try:
			exception_obj = AvailabilityException.objects.get(
				parent_availability=premises.availability,
				exception_datetime_start=datetime_start,
				exception_datetime_end=datetime_end
			)
		except AvailabilityException.DoesNotExist:

			exception_obj = AvailabilityException(
				parent_availability=premises.availability,
				exception_datetime_start=datetime_start,
				exception_datetime_end=datetime_end
			)
			exception_obj.save()
		return exception_obj


class CalendarSerializer(serializers.Serializer):
	number_of_slots = serializers.IntegerField()
	date = serializers.DateField()
	available = serializers.BooleanField()

