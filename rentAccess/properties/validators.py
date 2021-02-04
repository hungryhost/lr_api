from rest_framework import serializers
from common.models import SupportedCity


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