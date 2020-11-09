from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
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
		fields = ('id', 'first_name', 'last_name', 'username', 'account_type', 'email')
		model = Profile


class ChangePasswordSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
	password2 = serializers.CharField(write_only=True, required=True)
	old_password = serializers.CharField(write_only=True, required=True)

	class Meta:
		model = User
		fields = ('old_password', 'password', 'password2')

	def validate(self, attrs):
		if attrs['old_password'] == attrs['password2']:
			raise serializers.ValidationError({"password": "New Password is the same as old"})
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError({"password": "Password fields didn't match"})
		return attrs

	def validate_old_password(self, value):
		user = self.context['request'].user
		if not user.check_password(value):
			raise serializers.ValidationError("Invalid old password")
		return value

	def update(self, instance, validated_data):
		user = self.context['request'].user
		if user.pk != instance.pk:
			raise serializers.ValidationError({"Authorize": "You dont have permission for this user."})
		instance.set_password(validated_data['password'])
		instance.save()
		return instance
