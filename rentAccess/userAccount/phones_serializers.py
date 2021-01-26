import datetime
from time import timezone

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Phones


class PhonesSerializer(serializers.ModelSerializer):
	phone_number = serializers.CharField(max_length=13, required=False)
	phone_type = serializers.CharField(max_length=20, required=False)

	class Meta:
		model = Phones
		fields = [
			'phone_number',
			'phone_type',
		]

