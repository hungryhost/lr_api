from rest_framework import serializers
from common.models import SupportedCity
from datetime import datetime, timedelta, time, date


def validate_price(price: float):
	"""
	This method takes a price and checks against constraints.

	:param price: float number.

	"""
	if price <= 0:
		raise serializers.ValidationError(
			"Price cannot be zero or less than a zero"
		)
	if price > 99999:
		raise serializers.ValidationError(
			"Price cannot be that high"
		)


def validate_city(city: str):
	try:
		city = SupportedCity.objects.get(name=city)
	except SupportedCity.DoesNotExist:
		raise serializers.ValidationError(
			"City with given name is not supported."
		)


def validate_available_time(
		input_time
):
	try:
		if input_time.minute != 0:
			raise serializers.ValidationError(
				"Time must not have minutes"
			)
	except Exception as e:
		raise serializers.ValidationError(
				str(e)
			)