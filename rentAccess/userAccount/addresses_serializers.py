from rest_framework import serializers

from .models import BillingAddress


class BillingAddressSerializer(serializers.ModelSerializer):
	addr_type = serializers.CharField(max_length=100, required=True)
	addr_country = serializers.CharField(max_length=100, required=True)
	addr_city = serializers.CharField(max_length=100, required=True)
	addr_street_1 = serializers.CharField(max_length=100, required=True)
	addr_street_2 = serializers.CharField(max_length=100, required=False)
	addr_building = serializers.CharField(max_length=20, required=True)
	addr_floor = serializers.CharField(max_length=20, required=True)
	addr_number = serializers.CharField(max_length=30, required=True)
	zip_code = serializers.CharField(max_length=10, required=True)
	addr_is_active = serializers.BooleanField(required=False)

	class Meta:
		model = BillingAddress
		fields = [
			'addr_type',
			'addr_country',
			'addr_city',
			'addr_street_1',
			'addr_street_2',
			'addr_building',
			'addr_floor',
			'addr_number',
			'zip_code',
			'addr_is_active'
		]