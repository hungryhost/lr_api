from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Profile, UserImages
from .validators import email_validation
from django.contrib.auth import get_user_model
# TODO: add read only fields


class ProfileSerializer(serializers.ModelSerializer):
	account_type = serializers.CharField()
	is_confirmed = serializers.BooleanField()
	id_document = serializers.CharField()
	dob = serializers.DateField()
	main_address = serializers.CharField()
	patronymic = serializers.CharField(read_only=False)
	gender = serializers.CharField()

	class Meta:
		model = Profile
		fields = (
			'account_type',
			'is_confirmed',
			'id_document',
			'dob',
			'main_address',
			'patronymic',
			'gender',
		)


class ProfileListSerializer(serializers.ModelSerializer):
	username = serializers.CharField(read_only=True, source='user.username')
	email = serializers.CharField(read_only=True, source='user.email')
	id = serializers.IntegerField(source='user.id', read_only=True)

	class Meta:
		fields = ('id', 'username', 'email')
		model = Profile

"""
class UserUpdateSerializer(serializers.ModelSerializer):
	username = serializers.CharField(required=False, read_only=True)
	first_name = serializers.CharField(required=False, read_only=False)
	last_name = serializers.CharField(required=False, read_only=False)
	email = serializers.EmailField(required=False, read_only=True)
	id = serializers.IntegerField(required=False, read_only=True)
	profile = ProfileSerializer(many=False)

	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'username', 'email', 'profile')

	def update(self, instance, validated_data):
		first_name = validated_data.get("first_name", None)
		last_name = validated_data.get("last_name", None)
		email = validated_data.get("last_name", None)
		if first_name is not None:
			instance.first_name = validated_data['first_name']
		if last_name is not None:
			instance.last_name = validated_data['last_name']
		if email is not None:
			instance.email = validated_data['email']
		instance.save()
		return instance
"""


class ProfileUpdateSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(source='user.id', read_only=True)
	username = serializers.CharField(read_only=True, source='user.username')
	email = serializers.CharField(read_only=True, source='user.email')
	first_name = serializers.CharField(read_only=False, required=False)

	last_name = serializers.CharField(read_only=False, required=False)
	account_type = serializers.CharField(read_only=False, required=False)
	is_confirmed = serializers.BooleanField(read_only=True, required=False)
	id_document = serializers.CharField(read_only=False, required=False)
	dob = serializers.DateField(read_only=False, required=False)
	main_address = serializers.CharField(read_only=False, required=False)
	patronymic = serializers.CharField(read_only=False, required=False)
	gender = serializers.CharField(read_only=False, required=False)
	date_created = serializers.DateTimeField(source='user.date_joined', read_only=True)

	def update(self, instance, validated_data):
		user_object = User.objects.get(id=self.context['request'].user.id)
		first_name = validated_data.get('first_name', None)
		last_name = validated_data.get('last_name', None)
		account_type = validated_data.get('account_type', None)
		id_document = validated_data.get('id_document', None)
		dob = validated_data.get('dob', None)
		main_address = validated_data.get('main_address', None)
		patronymic = validated_data.get('patronymic', None)
		gender = validated_data.get('gender', None)

		if first_name is not None:
			user_object.first_name = first_name
			instance.first_name = first_name
		if last_name is not None:
			user_object.last_name = last_name
			instance.last_name = last_name
		if account_type is not None:
			instance.account_type = account_type
		if id_document is not None:
			instance.id_document = id_document
		if dob is not None:
			instance.dob = dob
		if main_address is not None:
			instance.main_address = main_address
		if patronymic is not None:
			instance.patronymic = patronymic
		if gender is not None:
			instance.gender = gender

		instance.save()
		user_object.save()
		return instance

	class Meta:
		model = Profile
		fields = (
			'id',
			'username',
			'email',
			'first_name',
			'last_name',
			'patronymic',
			'account_type',
			'is_confirmed',
			'id_document',
			'dob',
			'main_address',
			'gender',
			'date_created'
		)


class ProfileDetailSerializer(serializers.ModelSerializer):
	username = serializers.CharField(read_only=True, source='user.username')
	first_name = serializers.CharField(read_only=True, source='user.first_name')
	last_name = serializers.CharField(read_only=True, source='user.last_name')
	email = serializers.EmailField(read_only=True, source='user.email')
	id = serializers.IntegerField(source='user.id', read_only=True)
	date_created = serializers.DateTimeField(source='user.date_joined', read_only=True)
	# profilePicture
	account_type = serializers.CharField(read_only=True)
	is_confirmed = serializers.BooleanField(read_only=True)
	id_document = serializers.CharField(read_only=True)
	dob = serializers.DateField(read_only=True)
	main_address = serializers.CharField(read_only=True)
	patronymic = serializers.CharField(read_only=True)
	gender = serializers.CharField(read_only=True)

	class Meta:
		fields = (
			'id',
			'username',
			'email',
			'first_name',
			'last_name',
			'patronymic',
			'account_type',
			'is_confirmed',
			'id_document',
			'dob',
			'main_address',
			'gender',
			'date_created')
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


class FileUploadSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserImages
		fields = ('account', 'filepath', 'is_deleted', 'uploaded_at')
		read_only_fields = ['account']
