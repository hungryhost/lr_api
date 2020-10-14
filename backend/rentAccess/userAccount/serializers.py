from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

# TODO: add read only fields
#
#
#
#
#
#
#


class ProfileSerializer(serializers.ModelSerializer):
	username = serializers.CharField(read_only=True, source='user.username')
	first_name = serializers.CharField(read_only=True, source='user.first_name')
	last_name = serializers.CharField(read_only=True, source='user.last_name')
	email = serializers.CharField(read_only=True, source='user.email')
	id = serializers.IntegerField(source='user.id', read_only=True)

	class Meta:
		fields = ('id', 'first_name', 'last_name', 'username', 'owner', 'email')
		model = Profile
