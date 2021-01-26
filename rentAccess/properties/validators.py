from rest_framework import serializers


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

