import datetime
from time import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import (
	UserImage,
	BillingAddress, Document, PlanRequests, PlannedClient
)

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
	timezone = TimeZoneSerializerField(required=False, read_only=True)

	class Meta:
		model = User
		fields = [
			'id',
			'email',
			'first_name',
			'last_name',
			'middle_name',
			'timezone'
		]


class UserImagesSerializer(serializers.ModelSerializer):
	filepath = serializers.CharField(max_length=200, required=True)
	uploaded_at = serializers.DateTimeField(required=False)

	class Meta:
		model = UserImage
		fields = [
			'filepath',
			'uploaded_at',
		]


class ProfileUpdateSerializer(serializers.ModelSerializer):
	first_name = serializers.CharField(required=False, max_length=50)
	last_name = serializers.CharField(required=False, max_length=50)
	middle_name = serializers.CharField(max_length=50,
			read_only=False, required=False, allow_blank=True)
	dob = serializers.DateField(read_only=False, required=False, allow_null=True)
	gender = serializers.CharField(max_length=1,
			read_only=False, required=False, allow_blank=True)
	bio = serializers.CharField(read_only=False, max_length=1024, required=False, allow_blank=True)
	timezone = TimeZoneSerializerField(required=False)
	phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
	userpic = serializers.SerializerMethodField('get_userpic', default="")

	plan = serializers.SerializerMethodField("get_plan")
	work_email = serializers.EmailField(allow_null=True, allow_blank=True)
	use_work_email_incbookings = serializers.BooleanField()
	use_work_email_outbookings = serializers.BooleanField()
	show_work_email_in_contact_info = serializers.BooleanField()

	def get_plan(self, obj):
		try:
			plan = obj.user_plans.last()
			return plan.plan.code
		except Exception as e:
			return "DEFAULT"

	def get_userpic(self, obj):
		try:
			image_object = UserImage.objects.get(account=self.context['request'].user, is_deleted=False)
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

	class Meta:
		fields = [
			'id',
			'email',
			'phone',
			'userpic',
			'first_name',
			'last_name',
			'middle_name',
			'bio',
			'timezone',
			'plan',
			'work_email',
			'use_work_email_incbookings',
			'use_work_email_outbookings',
			'show_work_email_in_contact_info',
			'email_confirmed',
			'phone_confirmed',
			'client_rating',
			'is_banned',
			'last_password_update',
			'tos_version',
			'two_factor_auth',
			'is_staff',
			'dob',
			'gender',
			'created_at',
			'updated_at',
			# 'emails_url',
		]
		model = User


class ProfileDetailSerializer(serializers.ModelSerializer):
	userpic = serializers.SerializerMethodField('get_userpic', default="")
	timezone = TimeZoneSerializerField()
	plan = serializers.SerializerMethodField("get_plan")
	work_email = serializers.EmailField()
	use_work_email_incbookings = serializers.BooleanField()
	use_work_email_outbookings = serializers.BooleanField()
	show_work_email_in_contact_info = serializers.BooleanField()

	def get_plan(self, obj):
		try:
			plan = obj.user_plans.last()
			return plan.plan.code
		except Exception as e:
			return "DEFAULT"

	def get_userpic(self, obj):
		try:
			image_object = UserImage.objects.get(account=self.context['request'].user, is_deleted=False)
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
			'phone',
			'userpic',
			'first_name',
			'last_name',
			'middle_name',
			'bio',
			'timezone',
			'plan',
			'work_email',
			'use_work_email_incbookings',
			'use_work_email_outbookings',
			'show_work_email_in_contact_info',
			'email_confirmed',
			'phone_confirmed',
			'client_rating',
			'is_banned',
			'last_password_update',
			'tos_version',
			'two_factor_auth',
			'is_staff',
			'dob',
			'gender',
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
		instance.last_password_update = datetime.datetime.now()
		instance.save()
		return instance


class FileUploadSerializer(serializers.ModelSerializer):
	image = serializers.ImageField(required=True)

	class Meta:
		model = UserImage
		fields = ('account', 'image', 'is_deleted', 'uploaded_at')
		read_only_fields = ['account']

	def create(self, validated_data):
		# TODO: separate update mechanisms
		image = validated_data.get('image', None)
		if not UserImage.objects.filter(account=self.context['request'].user).exists():
			user_image_object = UserImage.objects.create(
				account=self.context['request'].user,
				image=image)
			return user_image_object
		else:
			UserImage.objects.filter(account=self.context['request'].user).delete()
			UserImage.objects.create(
				account=self.context['request'].user,
				image=image,
				uploaded_at=datetime.datetime.now()
			)
			return UserImage.objects.get(account=self.context['request'].user)


class UserPlanRequestCreateSerializer(serializers.ModelSerializer):

	class Meta:
		model = PlanRequests
		fields = [
			'requested_plan',
			'client',
			'status',
			'status_changed_reason',
			'created_at',
			'updated_at'
		]
		read_only_fields = [
			'requested_plan',
			'client',
			'status',
			'status_changed_reason',
			'created_at',
			'updated_at'
		]


class UserPlanSerializer(serializers.ModelSerializer):
	class Meta:
		model = PlannedClient
		fields = [
			'plan',
			'created_at',
			'updated_at'
		]
		read_only_fields = [
			'plan',
			'created_at',
			'updated_at'
		]