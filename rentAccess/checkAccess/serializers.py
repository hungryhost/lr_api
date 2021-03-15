from django.http import Http404
from rest_framework import serializers
from register.models import Lock
from properties.models import LockWithProperty
from .models import AccessLog


class AccessListSerializer(serializers.ModelSerializer):

	class Meta:
		model = AccessLog
		fields = '__all__'
