import datetime
from time import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import serializers
from .models import (
	Profile,
	UserImages,
	BillingAddresses, Documents
)


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


class ProfileSerializer(serializers.ModelSerializer):
	# using nested serializers for convenience
	account_type = serializers.CharField()
	is_confirmed = serializers.BooleanField()
	dob = serializers.DateField()
	patronymic = serializers.CharField(read_only=False)
	gender = serializers.CharField()

	class Meta:
		model = Profile
		fields = (
			'account_type',
			'is_confirmed',
			'dob',
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


class ProfileUpdateSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(source='user.id', read_only=True)
	username = serializers.CharField(read_only=True, source='user.username')
	email = serializers.CharField(read_only=True, source='user.email')
	is_confirmed = serializers.BooleanField(read_only=True, required=False)
	last_updated = serializers.DateTimeField(read_only=True)
	first_name = serializers.CharField(source='user.first_name')
	last_name = serializers.CharField(source='user.last_name')
	userpic = serializers.SerializerMethodField('get_userpic', default="")
	account_type = serializers.CharField(max_length=100,
										 read_only=False, required=False)
	dob = serializers.DateField(read_only=False, required=False)
	patronymic = serializers.CharField(max_length=50,
									   read_only=False, required=False)
	gender = serializers.CharField(max_length=1,
								   read_only=False, required=False)
	date_created = serializers.DateTimeField(source='user.date_joined', read_only=True)
	bio = serializers.CharField(read_only=False, max_length=1024, required=False)

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
			return self.context.get('request').build_absolute_uri(reverse('userAccount:user-details')) + '{id}/documents/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_billing_addresses_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/billing_addresses/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_phones_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/phones/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_emails_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/emails/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_properties_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/properties/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def to_representation(self, data):
		# consider overriding it further in order to enforce permissions
		representation = super(ProfileUpdateSerializer, self).to_representation(data)
		return representation

	def update(self, instance, validated_data):
		user_data = validated_data.pop('user', None)

		user_inst_fields = {}
		if user_data:
			first_name = user_data.pop('first_name', None)
			last_name = user_data.pop('last_name', None)
			if first_name:
				user_inst_fields['first_name'] = first_name
				instance.user.first_name = first_name
			if last_name:
				user_inst_fields['last_name'] = last_name
				instance.user.last_name = last_name
		account_type = validated_data.get('account_type', None)
		dob = validated_data.get('dob', None)
		patronymic = validated_data.get('patronymic', None)
		gender = validated_data.get('gender', None)
		bio = validated_data.get('bio', None)
		if user_inst_fields:
			User.objects.update_or_create(id=instance.user.id, defaults=user_inst_fields)
		if account_type is not None:
			instance.account_type = account_type
		if dob is not None:
			instance.dob = dob
		if patronymic is not None:
			instance.patronymic = patronymic
		if gender is not None and gender in ['M', 'F']:
			instance.gender = gender
		if bio is not None:
			instance.bio = bio
		instance.last_updated = now()
		instance.save()
		return instance

	class Meta:
		fields = [
			'id',
			'username',
			'email',
			'userpic',
			'first_name',
			'last_name',
			'patronymic',
			'bio',
			'account_type',
			'is_confirmed',
			'dob',
			'gender',
			'properties_url',
			'documents_url',
			'billing_addresses_url',
			'phones_url',
			# 'emails_url',
			'date_created',
			'last_updated'
		]
		model = Profile


class ProfileDetailSerializer(serializers.ModelSerializer):
	username = serializers.CharField(read_only=True, source='user.username')
	first_name = serializers.CharField(read_only=True, source='user.first_name')
	last_name = serializers.CharField(read_only=True, source='user.last_name')
	email = serializers.EmailField(read_only=True, source='user.email')
	id = serializers.IntegerField(source='user.id', read_only=True)
	date_created = serializers.DateTimeField(source='user.date_joined', read_only=True)
	last_updated = serializers.DateTimeField(read_only=True)
	account_type = serializers.CharField(read_only=True, max_length=100)
	is_confirmed = serializers.BooleanField(read_only=True)
	dob = serializers.DateField(read_only=True, initial="", default="")
	patronymic = serializers.CharField(read_only=True, max_length=50)
	gender = serializers.CharField(read_only=True, max_length=1)
	bio = serializers.CharField(read_only=True, max_length=1024)
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
			return self.context.get('request').build_absolute_uri(reverse('userAccount:user-details')) + '{id}/documents/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_billing_addresses_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/billing_addresses/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_phones_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/phones/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_emails_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/emails/'.format(id=obj.user.id)
		except Exception as e:
			return str(e)

	def get_properties_url(self, obj):
		try:
			return self.context['request'].build_absolute_uri(reverse('userAccount:user-details')) + '{id}/properties/'.format(id=obj.user.id)
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
			'username',
			'email',
			'userpic',
			'first_name',
			'last_name',
			'patronymic',
			'bio',
			'account_type',
			'is_confirmed',
			'dob',
			'gender',
			'properties_url',
			'documents_url',
			'billing_addresses_url',
			'phones_url',
			# 'emails_url',
			'date_created',
			'last_updated'
		]
		model = Profile


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
