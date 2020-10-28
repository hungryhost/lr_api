<<<<<<< HEAD
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

=======
# from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile


>>>>>>> backend-profile
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
<<<<<<< HEAD
		fields = ('id', 'first_name', 'last_name', 'username', 'owner', 'email')
=======
		fields = ('id', 'first_name', 'last_name', 'username', 'account_type', 'email')
>>>>>>> backend-profile
		model = Profile
