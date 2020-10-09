from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

# TODO: add additional serializers for different kind of requests
#
#
#
#
#
#
#
#


class ProfileSerializer(serializers.ModelSerializer):
	username = serializers.CharField(read_only=True, source='user.username')
	email = serializers.CharField(read_only=True, source='user.email')
	id = serializers.IntegerField(source='user.id', read_only=True)

	class Meta:
		fields = ('id', 'username', 'owner', 'email')
		model = Profile
