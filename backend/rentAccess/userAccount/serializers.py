from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import (
	Profile,
	UserImages,
	BillingAddresses,
	Documents, Phones, DocumentTypes
)
# TODO: add validation for each field with documents
# TODO: add urls for properties


class PhonesSerializer(serializers.ModelSerializer):
	phone_number = serializers.CharField(max_length=13, required=False)
	phone_type = serializers.CharField(max_length=20, required=False)

	class Meta:
		model = Phones
		fields = [
			'phone_number',
			'phone_type',
		]


class UserImagesSerializer(serializers.ModelSerializer):
	filepath = serializers.CharField(max_length=200, required=False)
	uploaded_at = serializers.DateTimeField(required=False)

	class Meta:
		model = UserImages
		fields = [
			'filepath',
			'uploaded_at',
		]


class DocumentsSerializer(serializers.ModelSerializer):
	doc_type = serializers.CharField(max_length=100, required=False)
	doc_serial = serializers.IntegerField(required=False)
	doc_number = serializers.IntegerField(required=False)
	doc_issued_at = serializers.DateField(required=False)
	doc_issued_by = serializers.CharField(max_length=100, required=False)
	doc_is_confirmed = serializers.BooleanField(required=False)

	class Meta:
		model = Documents
		fields = [
			'id',
			'doc_type',
			'doc_serial',
			'doc_number',
			'doc_issued_at',
			'doc_issued_by',
			'doc_is_confirmed'
		]


class BillingAddressSerializer(serializers.ModelSerializer):
	addr_type = serializers.CharField(max_length=100, required=False)
	addr_country = serializers.CharField(max_length=100, required=False)
	addr_city = serializers.CharField(max_length=100, required=False)
	addr_street_1 = serializers.CharField(max_length=100, required=False)
	addr_street_2 = serializers.CharField(max_length=100, required=False)
	addr_building = serializers.CharField(max_length=20, required=False)
	addr_floor = serializers.CharField(max_length=20, required=False)
	addr_number = serializers.CharField(max_length=30, required=False)
	zip_code = serializers.CharField(max_length=10, required=False)
	addr_is_active = serializers.BooleanField(required=False)

	class Meta:
		model = BillingAddresses
		fields = [
			'addr_type',
			'addr_country',
			'addr_city',
			'addr_street_1',
			'addr_street_2',
			'addr_building',
			'addr_floor',
			'addr_number',
			'zip_code',
			'addr_is_active'
		]


class ProfileSerializer(serializers.ModelSerializer):
	# using nested serializers for convenience
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


class ProfileUpdateSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(source='user.id', read_only=True)
	username = serializers.CharField(read_only=True, source='user.username')
	email = serializers.CharField(read_only=True, source='user.email')
	is_confirmed = serializers.BooleanField(read_only=True, required=False)
	last_updated = serializers.DateTimeField(read_only=True)
	first_name = serializers.CharField(read_only=False, required=False)
	last_name = serializers.CharField(read_only=False, required=False)
	account_type = serializers.CharField(max_length=100,
										read_only=False, required=False)
	dob = serializers.DateField(read_only=False, required=False)
	patronymic = serializers.CharField(max_length=50,
									read_only=False, required=False)
	gender = serializers.CharField(max_length=1,
								read_only=False, required=False)
	date_created = serializers.DateTimeField(source='user.date_joined', read_only=True)
	bio = serializers.CharField(read_only=False, max_length=1024, required=False)

	# documents = DocumentsSerializer(read_only=False, many=True)
	# billing_addresses = BillingAddressSerializer(read_only=False, many=False, required=False)
	# account_phones = PhonesSerializer(read_only=False, many=False, required=False)
	# account_images = UserImagesSerializer(read_only=True, many=True, required=False)

	def to_representation(self, data):
		representation = super(ProfileUpdateSerializer, self).to_representation(data)
		return representation

	def update(self, instance, validated_data):

		user_object = User.objects.get(id=self.context['request'].user.id)
		first_name = validated_data.get('first_name', None)
		last_name = validated_data.get('last_name', None)
		account_type = validated_data.get('account_type', None)
		dob = validated_data.get('dob', None)
		patronymic = validated_data.get('patronymic', None)
		gender = validated_data.get('gender', None)
		bio = validated_data.get('bio', None)

		if first_name is not None:
			user_object.first_name = first_name
			instance.first_name = first_name
		if last_name is not None:
			user_object.last_name = last_name
			instance.last_name = last_name
		if account_type is not None:
			instance.account_type = account_type
		if dob is not None:
			instance.dob = dob
		if patronymic is not None:
			instance.patronymic = patronymic
		if gender is not None:
			instance.gender = gender
		if bio is not None:
			instance.bio = bio

		user_object.save()
		instance.save()
		return instance

	class Meta:
		fields = [
			'id',
			'username',
			'email',
			'first_name',
			'last_name',
			'patronymic',
			'bio',
			'account_type',
			'is_confirmed',
			'dob',
			'gender',
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
	dob = serializers.DateField(read_only=True)
	patronymic = serializers.CharField(read_only=True, max_length=50)
	gender = serializers.CharField(read_only=True, max_length=1)
	bio = serializers.CharField(read_only=True, max_length=1024)
	userpic = serializers.SerializerMethodField('get_userpic')
	# documents = DocumentsSerializer(read_only=True, many=True)
	# billing_addresses = BillingAddressSerializer(read_only=True, many=True)
	# account_phones = PhonesSerializer(read_only=True, many=True)
	# account_images = UserImagesSerializer(read_only=True, many=True)

	def get_userpic(self, obj):
		image_object = UserImages.objects.get(account=obj, is_deleted=False)
		request = self.context.get('request')
		return request.build_absolute_uri(image_object.image.url)


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
		fields = ('account', 'image', 'is_deleted', 'uploaded_at')
		read_only_fields = ['account']

	def create(self, validated_data):
		image = validated_data.get('image', None)
		user_image_object = UserImages.objects.create(
			account=Profile.objects.get(user=self.context['request'].user),
			image=image
		)
		return user_image_object
