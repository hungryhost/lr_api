import datetime
from time import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import (
	UserImages,
	BillingAddresses, Documents
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = (
			'first_name',
			'last_name'
		)


class UserImagesSerializer(serializers.ModelSerializer):
	filepath = serializers.CharField(max_length=200, required=True)
	uploaded_at = serializers.DateTimeField(required=False)

	class Meta:
		model = UserImages
		fields = [
			'filepath',
			'uploaded_at',
		]


class ProfileUpdateSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(required=False, max_length=50)
	last_name = serializers.CharField(required=False, max_length=50)
	middle_name = serializers.CharField(max_length=50,
			read_only=False, required=False)
	dob = serializers.DateField(read_only=False, required=False)
	gender = serializers.CharField(max_length=1,
			read_only=False, required=False)
	bio = serializers.CharField(read_only=False, max_length=1024, required=False)
	timezone = TimeZoneSerializerField(required=False)

	userpic = serializers.SerializerMethodField('get_userpic', default="")
	documents_url = serializers.SerializerMethodField('get_documents_url')
	billing_addresses_url = serializers.SerializerMethodField('get_billing_addresses_url')
	phones_url = serializers.SerializerMethodField('get_phones_url')
	# emails_url = serializers.SerializerMethodField('get_emails_url')
	properties_url = serializers.SerializerMethodField('get_properties_url')

	def get_userpic(self, obj):
		try:
			image_object = UserImages.objects.get(account=self.context['request'].user, is_deleted=False)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception as e:
			return ""

	def get_documents_url(self, obj):
		try:
			return self.context.get('request').build_absolute_uri(
				reverse('userAccount:user-details')) + 'documents/'
		except Exception as e:
			return str(e)

	def get_billing_addresses_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'billing_addresses/'
		except Exception as e:
			return str(e)

	def get_phones_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'phones/'
		except Exception as e:
			return str(e)

	def get_emails_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'emails/'
		except Exception as e:
			return str(e)

	def get_properties_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'properties/'
		except Exception as e:
			return str(e)

	def to_representation(self, data):
		# consider overriding it further in order to enforce permissions
		representation = super(ProfileUpdateSerializer, self).to_representation(data)
		return representation

	def update(self, instance, validated_data):
		first_name = validated_data.get('first_name', None)
		last_name = validated_data.get('last_name', None)
		middle_name = validated_data.get('middle_name', None)

		dob = validated_data.get('dob', None)
		gender = validated_data.get('gender', None)
		bio = validated_data.get('bio', None)
		_timezone = validated_data.get('timezone', None)

		if dob:
			instance.dob = dob
		if middle_name:
			instance.middle_name = middle_name
		if gender and gender in ['M', 'F']:
			instance.gender = gender
		if bio is not None:
			instance.bio = bio
		if first_name:
			instance.first_name = first_name
		if last_name:
			instance.last_name = last_name
		instance.updated_at = now()
		instance.save()
		return instance

	class Meta:
		fields = [
			'id',
			'email',
			'userpic',
			'first_name',
			'last_name',
			'middle_name',
			'bio',
			'timezone',
			'is_confirmed',
			'two_factor_auth',
			'is_staff',
			'dob',
			'gender',
			'properties_url',
			'documents_url',
			'billing_addresses_url',
			'phones_url',
			'created_at',
			'updated_at',
			# 'emails_url',
		]
		model = User


class ProfileDetailSerializer(serializers.ModelSerializer):
	userpic = serializers.SerializerMethodField('get_userpic', default="")
	documents_url = serializers.SerializerMethodField('get_documents_url')
	billing_addresses_url = serializers.SerializerMethodField('get_billing_addresses_url')
	phones_url = serializers.SerializerMethodField('get_phones_url')
	# emails_url = serializers.SerializerMethodField('get_emails_url')
	properties_url = serializers.SerializerMethodField('get_properties_url')
	timezone = TimeZoneSerializerField()

	def get_userpic(self, obj):
		try:
			image_object = UserImages.objects.get(account=self.context['request'].user, is_deleted=False)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception as e:
			return ""

	def get_documents_url(self, obj):
		try:
			return self.context.get('request').build_absolute_uri(
				reverse('userAccount:user-details')) + 'documents/'
		except Exception as e:
			return str(e)

	def get_billing_addresses_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'billing_addresses/'
		except Exception as e:
			return str(e)

	def get_phones_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'phones/'
		except Exception as e:
			return str(e)

	def get_emails_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'emails/'
		except Exception as e:
			return str(e)

	def get_properties_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(
				reverse('userAccount:user-details')) + 'properties/'
		except Exception as e:
			return str(e)

	def to_representation(self, data):
		representation = super(ProfileDetailSerializer, self).to_representation(data)
		"""
		if self.context['request'].GET.get('expand_all'):
			return representation
		if not self.context['request'].GET.get('expand_images'):
			representation.pop("account_images",)
		if not self.context['request'].GET.get('expand_docs'):
			representation.pop("documents",)
		if not self.context['request'].GET.get('expand_phones'):
			representation.pop("account_phones",)
		if not self.context['request'].GET.get('expand_addresses'):
			representation.pop("billing_addresses",)
		"""
		return representation

	class Meta:
		fields = [
			'id',
			'email',
			'userpic',
			'first_name',
			'last_name',
			'middle_name',
			'bio',
			'timezone',
			'is_confirmed',
			'two_factor_auth',
			'is_staff',
			'dob',
			'gender',
			'properties_url',
			'documents_url',
			'billing_addresses_url',
			'phones_url',
			'created_at',
			'updated_at',
			# 'emails_url',
		]
		model = User


class ChangePasswordSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
	password2 = serializers.CharField(write_only=True, required=True)
	old_password = serializers.CharField(write_only=True, required=True)

	class Meta:
		model = User
		fields = ('old_password', 'password', 'password2')

	def validate(self, attrs):
		if attrs['password'] != attrs['password2']:
			raise serializers.ValidationError({"password": "Password fields didn't match"})
		if attrs['old_password'] == attrs['password2']:
			raise serializers.ValidationError({"password": "New Password is the same as old"})
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
	image = serializers.ImageField(required=True)

	class Meta:
		model = UserImages
		fields = ('account', 'image', 'is_deleted', 'uploaded_at')
		read_only_fields = ['account']

	def create(self, validated_data):
		# TODO: separate update mechanisms
		image = validated_data.get('image', None)
		if not UserImages.objects.filter(account=self.context['request'].user).exists():
			user_image_object = UserImages.objects.create(
				account=self.context['request'].user,
				image=image)
			return user_image_object
		else:
			UserImages.objects.filter(account=self.context['request'].user).delete()
			UserImages.objects.create(
				account=self.context['request'].user,
				image=image,
				uploaded_at=datetime.datetime.now()
			)
			return UserImages.objects.get(account=self.context['request'].user)
