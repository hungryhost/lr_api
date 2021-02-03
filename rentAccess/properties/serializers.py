from abc import ABC

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import serializers, status
from common.models import SupportedCities
import logging

from .logger_helpers import get_client_ip
from .models import Property, PremisesAddresses, PremisesImages, Ownership, Availability
from .validators import validate_price, validate_city
from .availability_utils import available_days_to_db, available_days_from_db, available_hours_to_db

#
#
User = get_user_model()
crud_logger_info = logging.getLogger('rentAccess.properties.crud.info')
owners_logger = logging.getLogger('rentAccess.properties.owners.info')
bookings_logger = logging.getLogger('rentAccess.properties.bookings.info')
images_logger = logging.getLogger('rentAccess.properties.images.info')


class DaysListField(serializers.ListField):
	child = serializers.IntegerField(min_value=0, max_value=6)


class AvailabilityCreateSerializer(serializers.Serializer):
	open_days = DaysListField(required=True, allow_empty=True, max_length=7)
	departure_time_until = serializers.TimeField(required=False)
	arrival_time_from = serializers.TimeField(required=False)
	maximum_number_of_clients = serializers.IntegerField(min_value=1, required=True)
	available_until = serializers.TimeField(required=False)
	available_from = serializers.TimeField(required=False)
	booking_interval = serializers.IntegerField(required=False)


class AvailabilityDailySerializer(serializers.ModelSerializer):
	departure_time_until = serializers.TimeField(required=False, source='available_until')
	arrival_time_from = serializers.TimeField(required=False, source='available_from')
	maximum_number_of_clients = serializers.IntegerField(min_value=1, required=True)

	class Meta:
		model = Availability
		fields = [
			'open_days',
			'departure_time_until',
			'arrival_time_from',
			'maximum_number_of_clients',
		]

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['open_days'] = available_days_from_db(instance.open_days)
		return representation


class AvailabilityHourlySerializer(serializers.ModelSerializer):
	available_until = serializers.TimeField(format="%H:%M", required=False)
	available_from = serializers.TimeField(format="%H:%M", required=False)
	maximum_number_of_clients = serializers.IntegerField(min_value=1, required=True)

	class Meta:
		model = Availability
		fields = [
			'open_days',
			'available_until',
			'available_from',
			'maximum_number_of_clients'
		]

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		representation['open_days'] = available_days_from_db(instance.open_days)
		return representation


class FilteringNotMainImagesListSerializer(serializers.ListSerializer):
	def to_representation(self, data):
		return super(FilteringNotMainImagesListSerializer, self).to_representation(data)


class FilteringContactsListSerializer(serializers.ListSerializer):
	def to_representation(self, data):
		data = data.filter(visibility=100)
		return super(FilteringContactsListSerializer, self).to_representation(data)


class PropertyOwnershipListSerializer(serializers.ModelSerializer):
	email = serializers.CharField(read_only=True, source='user.email')
	first_name = serializers.CharField(source='user.first_name', read_only=True)
	last_name = serializers.CharField(source='user.last_name', read_only=True)
	middle_name = serializers.CharField(max_length=50, source='user.middle_name',
	                                   read_only=True)

	class Meta:
		model = Ownership
		fields = (
			'user',
			'email',
			'first_name',
			'last_name',
			'middle_name',
			'is_creator',
			'permission_level',
			'created_at',
			'updated_at'
		)


class PropertyOwnershipAddSerializer(serializers.ModelSerializer):
	email = serializers.CharField(read_only=False, source='user.email', required=True)
	permission_level = serializers.IntegerField(required=True)
	visibility = serializers.IntegerField(required=False)
	first_name = serializers.CharField(source='user.first_name', read_only=True)
	last_name = serializers.CharField(source='user.last_name', read_only=True)

	patronymic = serializers.CharField(max_length=50, source='user.profile.patronymic',
	                                   read_only=True)

	class Meta:
		model = Ownership
		fields = (
			'user',
			'visibility',
			'email',
			'first_name',
			'last_name',
			'patronymic',
			'is_creator',
			'permission_level',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'user',
			'first_name',
			'last_name',
			'patronymic',
			'is_creator',
			'created_at',
			'updated_at'
		]

	def create(self, validated_data):
		email = validated_data.get("email", None)
		permission_level = validated_data.get("email", None)
		visibility = validated_data.get("visibility", None)
		try:
			user = User.objects.get(email=email)
		except User.DoesNotExist:
			raise serializers.ValidationError({
				"user: user with given email does not exist."
			})

		if not visibility:
			visibility = 250
		obj = Ownership.objects.create(
			premises_id=self.context["property_id"],
			user=user,
			is_creator=False,
			visibility=visibility,
			permission_level_id=permission_level
		)
		owners_logger.info(
			f"object: owner; stage: serializer; action_type: create; user_id: {self.context['request'].user.id}; "
			f"property_id: {self.context['property_id']}; "
			f"owner_id: {obj.id}; ip_addr: {get_client_ip(self.context['request'])}; status: OK;")
		return obj


class PropertyOwnershipUpdateSerializer(serializers.ModelSerializer):
	email = serializers.CharField(read_only=True, source='user.email')
	permission_level = serializers.IntegerField(required=False)
	visibility = serializers.IntegerField(required=False)
	first_name = serializers.CharField(source='user.first_name', read_only=True)
	last_name = serializers.CharField(source='user.last_name', read_only=True)

	patronymic = serializers.CharField(max_length=50, source='user.profile.patronymic', read_only=True)

	class Meta:
		model = Ownership
		fields = (
			'user',
			'email',
			'first_name',
			'last_name',
			'patronymic',
			'is_creator',
			'permission_level',
			'created_at',
			'updated_at'
		)

	def update(self, instance, validated_data):
		permission_level = validated_data.get("email", None)
		visibility = validated_data.get("visibility", None)

		if permission_level:
			instance.permission_level = permission_level
		if visibility:
			instance.visibility = visibility
		instance.save()
		owners_logger.info(
			f"object: owner; stage: serializer; action_type: update; user_id: {self.context['request'].user.id}; "
			f"property_id: {self.context['property_id']}; "
			f"owner_id: {instance.id}; ip_addr: {get_client_ip(self.context['request'])}; status: OK;")
		return instance


class PropertyImagesSerializer(serializers.ModelSerializer):
	image = serializers.ImageField(required=True)
	is_main = serializers.BooleanField(required=False, read_only=False)

	class Meta:
		model = PremisesImages
		list_serializer_class = FilteringNotMainImagesListSerializer
		fields = (
			'id',
			'image',
			'is_main',
			'uploaded_at'
		)


class PropertyAddressesSerializer(serializers.ModelSerializer):
	country = serializers.CharField(max_length=100, required=True)
	city = serializers.CharField(max_length=100, required=True, source='city.name',
	                             validators=[validate_city])
	street = serializers.CharField(max_length=255, required=True)
	building = serializers.CharField(max_length=20, required=True)
	floor = serializers.CharField(max_length=20, required=True)
	number = serializers.CharField(max_length=30, required=True)
	zip_code = serializers.CharField(max_length=10, required=True)
	directions_description = serializers.CharField(max_length=500, required=False)

	class Meta:
		model = PremisesAddresses
		fields = (
			'country',
			'city',
			'street',
			'building',
			'floor',
			'number',
			'zip_code',
			'directions_description',
		)

	def to_internal_value(self, data):
		return super().to_internal_value(data)


class PropertyAddressesListSerializer(serializers.ModelSerializer):
	city = serializers.CharField(max_length=100, read_only=True, source='city.name')

	class Meta:
		model = PremisesAddresses
		fields = (
			'country',
			'city',
			'street',
			'building',
			'floor',
			'number',
			'zip_code',
			'directions_description',
		)


class PropertyListSerializer(serializers.ModelSerializer):
	property_address = PropertyAddressesSerializer(many=False, read_only=True)
	main_image = serializers.SerializerMethodField('get_main_image', read_only=True)
	id = serializers.IntegerField(read_only=True)
	client_greeting_message = serializers.CharField(required=False)

	class Meta:
		model = Property

		fields = (
			'id',
			'title',
			'body',
			'price',
			'active',
			'property_type',
			'main_image',
			'booking_type',
			'visibility',
			'property_address',
			'requires_additional_confirmation',
			'client_greeting_message',
			'created_at',
			'updated_at',
		)

		read_only_fields = ['id']

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception:
			return ""

	def get_owners_url(self, obj):
		try:
			return self.context.get('request').build_absolute_uri(
				reverse('properties:property-list')) + '{id}/owners/'.format(id=obj.pk)
		except Exception:
			return ""


class PropertySerializer(serializers.ModelSerializer):
	"""
	Serializer class for general purposes.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	availability = serializers.SerializerMethodField('get_availability')
	property_address = PropertyAddressesSerializer(many=False, read_only=True)
	property_images = PropertyImagesSerializer(many=True, read_only=True)
	contacts = serializers.SerializerMethodField('get_contacts')
	main_image = serializers.SerializerMethodField('get_main_image')
	id = serializers.IntegerField()
	can_edit = serializers.SerializerMethodField('get_can_edit')

	class Meta:
		model = Property

		fields = (
			'id',
			'title',
			'body',
			'price',
			'can_edit',
			'active',
			'booking_type',
			'availability',
			'property_type',
			'main_image',
			'contacts',
			'property_address',
			'property_images',
			'visibility',
			'requires_additional_confirmation',
			'client_greeting_message',
			'created_at',
			'updated_at'

		)
		read_only_fields = ['id']

	def get_contacts(self, obj):
		serializer = FilteringContactsListSerializer(obj.owners,
			child=PropertyOwnershipListSerializer())
		return serializer.data

	def get_availability(self, obj):
		if obj.booking_type == 100:
			serializer = AvailabilityDailySerializer(obj.availability)
			return serializer.data
		else:
			serializer = AvailabilityHourlySerializer(obj.availability)
			return serializer.data

	def get_can_edit(self, obj):
		if obj.owners.filter(user=self.context["request"].user).exists():
			return True
		else:
			return False

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception:
			return ""

	def get_owners_url(self, obj):
		try:
			return self.context.get('request').build_absolute_uri(
				reverse('properties:property-list')) + '{id}/owners/'.format(id=obj.pk)
		except Exception:
			return ""


class PropertyCreateSerializer(serializers.ModelSerializer):
	availability = AvailabilityCreateSerializer(many=False, required=True)
	title = serializers.CharField(required=True, max_length=50)
	body = serializers.CharField(required=True, max_length=500)
	price = serializers.IntegerField(allow_null=True, required=False, validators=[validate_price])
	active = serializers.BooleanField(required=False)
	property_address = PropertyAddressesSerializer(many=False, required=True)
	client_greeting_message = serializers.CharField(required=False, max_length=500)
	main_image = serializers.SerializerMethodField('get_main_image', read_only=True)
	visibility = serializers.IntegerField(required=True)
	requires_additional_confirmation = serializers.BooleanField(required=False)
	booking_type = serializers.IntegerField(required=True)

	class Meta:
		model = Property

		fields = [
			'id',
			'title',
			'body',
			'price',
			'active',
			'property_type',
			'main_image',
			'availability',
			'visibility',
			'property_address',
			'requires_additional_confirmation',
			'client_greeting_message',
			'booking_type',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['creator', 'id']

	def to_internal_value(self, data):
		return super().to_internal_value(data)

	def to_representation(self, instance):
		if instance.booking_type == 100:
			serializer = AvailabilityDailySerializer(instance.availability)
		if instance.booking_type == 200:
			serializer = AvailabilityHourlySerializer(instance.availability)
		representation = super().to_representation(instance)
		representation['availability'] = serializer.data
		return representation

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception:
			return ""

	def validate(self, attrs):
		if attrs['booking_type'] == 100:
			necessary_keys = [
				'arrival_time_from',
				'departure_time_until',
				'open_days',
				'maximum_number_of_clients',
			]
			availability = attrs['availability']
			keys = list(availability.keys())
			for key in necessary_keys:
				if key not in keys:
					raise serializers.ValidationError({
						"availability": "Not all attributed of daily availability are provided",
					})
		elif attrs['booking_type'] == 200:
			necessary_keys = [
				'available_from',
				'available_until',
				'open_days',
				'maximum_number_of_clients',
			]
			availability = attrs['availability']
			keys = list(availability.keys())

			for key in necessary_keys:
				if key not in keys:
					raise serializers.ValidationError({
						"availability": "Not all attributed of daily availability are provided",
					})
		else:
			raise serializers.ValidationError({
				"booking_type": "Invalid booking type.",
			})
		return super(PropertyCreateSerializer, self).validate(attrs)

	def create(self, validated_data):
		property_addresses = validated_data.pop('property_address')
		property_availability = validated_data.pop('availability')

		title = validated_data["title"]
		body = validated_data["body"]
		price = validated_data.get("price", None)
		visibility = validated_data.get("visibility", None)
		booking_type = validated_data.get("booking_type", None)
		property_type = validated_data["property_type"]
		active = validated_data.get("active", None)
		requires_additional_confirmation = validated_data.get("requires_additional_confirmation", None)
		if price is None:
			price = None
		if active is None:
			active = True
		if (visibility is None) or (visibility not in [100, 200, 300]):
			visibility = 100
		if not requires_additional_confirmation:
			requires_additional_confirmation = False
		property_to_create = Property.objects.create(
			title=title, body=body, price=price, active=active, property_type=property_type,
			booking_type=booking_type,
			visibility=visibility, requires_additional_confirmation=requires_additional_confirmation)

		PremisesAddresses.objects.create(
			premises=property_to_create,
			country=property_addresses['country'],
			city_id=property_addresses['city']['name'],
			street=property_addresses['street'],
			building=property_addresses['building'],
			floor=property_addresses['floor'],
			number=property_addresses['number'],
			zip_code=property_addresses['zip_code'],
			directions_description=property_addresses.get('directions_description', "")
		)
		open_days = available_days_to_db(property_availability["open_days"])

		maximum_number_of_clients = property_availability["maximum_number_of_clients"]
		booking_interval = 0
		available_hours = None
		if booking_type == 100:
			available_from = property_availability["arrival_time_from"]
			available_until = property_availability["departure_time_until"]
		if booking_type == 200:
			available_hours = available_hours_to_db(property_availability["available_from"],
			                                        property_availability["available_until"])
			available_from = property_availability["available_from"]
			available_until = property_availability["available_until"]
		Availability.objects.create(
			premises=property_to_create,
			open_days=open_days,
			booking_interval=booking_interval,
			maximum_number_of_clients=maximum_number_of_clients,
			available_from=available_from,
			available_until=available_until,
			available_hours=available_hours,
			)
		crud_logger_info.info(
			f"object: property; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {property_to_create.id}; "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")
		return property_to_create


class PropertyUpdateSerializer(serializers.ModelSerializer):
	availability = AvailabilityCreateSerializer(many=False, required=False)
	property_address = PropertyAddressesSerializer(many=False, required=False)
	property_images = PropertyImagesSerializer(many=True, required=False)
	contacts = FilteringContactsListSerializer(
		child=PropertyOwnershipListSerializer(), source='owners')
	main_image = serializers.SerializerMethodField('get_main_image')
	id = serializers.IntegerField(read_only=True)
	visibility = serializers.IntegerField(required=False)
	client_greeting_message = serializers.CharField(required=False, allow_blank=True)
	requires_additional_confirmation = serializers.BooleanField(required=False)

	class Meta:
		model = Property
		fields = (
			'id',
			'title',
			'body',
			'price',
			'active',
			'property_type',
			'availability',
			'main_image',
			'booking_type',
			'contacts',
			'property_address',
			'property_images',
			'visibility',
			'requires_additional_confirmation',
			'client_greeting_message',
			'created_at',
			'updated_at',

		)
		read_only_fields = ['id']

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception:
			return ""

	def to_representation(self, instance):
		if instance.booking_type == 100:
			serializer = AvailabilityDailySerializer(instance.availability)
		if instance.booking_type == 200:
			serializer = AvailabilityHourlySerializer(instance.availability)
		representation = super().to_representation(instance)
		representation['availability'] = serializer.data
		return representation

	def is_valid(self, raise_exception=False):
		ret = super(PropertyUpdateSerializer, self).is_valid(False)
		if self._errors:
			crud_logger_info.info(
				f"object: property; stage: serialization; action_type: update; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def update(self, instance, validated_data):
		"""
		Explicitly created method. Seed docs on serializers.
		:param instance
		:param validated_data
		:return: instance
		"""
		address_data = validated_data.pop("property_address", None)
		availability_data = validated_data.pop("availability", None)
		title = validated_data.get("title", None)
		body = validated_data.get("body", None)
		price = validated_data.get("price", None)
		active = validated_data.get("active", None)
		visibility = validated_data.get("visibility", None)
		property_type_id = validated_data.get("property_type_id", None)
		requires_additional_confirmation = validated_data.get("requires_additional_confirmation", None)
		greeting_message = validated_data.get("client_greeting_message")
		if greeting_message or greeting_message == "":
			instance.client_greeting_message = greeting_message
		if title:
			instance.title = title
		if body:
			instance.body = body
		if price:
			instance.price = price
		if active:
			instance.active = active
		if visibility:
			instance.visibility = visibility
		if property_type_id:
			instance.property_type_id = property_type_id
		if requires_additional_confirmation:
			instance.requires_additional_confirmation = requires_additional_confirmation
		if availability_data:
			availability_to_update = Availability.objects.get(premises_id=instance.id)
			available_days_from_request = availability_data.get("open_days", None)
			if available_days_from_request:
				open_days = available_days_to_db(available_days_from_request)
			else:
				open_days = None
			maximum_number_of_clients = availability_data.get("maximum_number_of_clients", None)
			if open_days:
				availability_to_update.open_days = open_days
			if maximum_number_of_clients:
				availability_to_update.maximum_number_of_clients = maximum_number_of_clients
			if instance.booking_type == 100:
				available_from = availability_data.get("arrival_time_from", None)
				available_until = availability_data.get("departure_time_until", None)
				if available_from:
					availability_to_update.available_from = available_from
				if available_until:
					availability_to_update.available_until = available_until
			if instance.booking_type == 200:
				booking_interval = availability_data.get("booking_interval", None)
				available_from = availability_data.get("available_from", None)
				available_until = availability_data.get("available_until", None)
				if booking_interval:
					availability_to_update.booking_interval = booking_interval
				if available_from:
					availability_to_update.available_from = available_from
				if available_until:
					availability_to_update.available_until = available_until
			availability_to_update.save()
		if address_data:
			address_to_update = PremisesAddresses.objects.get(premises_id=instance.id)
			country = address_data.get('country', None)
			paddr_city = address_data.get('city', None)
			paddr_street = address_data.get('street', None)
			paddr_building = address_data.get('building', None)
			paddr_floor = address_data.get('floor', None)
			paddr_number = address_data.get('number', None)
			pzip_code = address_data.get('zip_code', None)
			if country:
				address_to_update.country = country
			if paddr_city:
				validate_city(paddr_city)
				address_to_update.city = paddr_city
			if paddr_street:
				address_to_update.street = paddr_street
			if paddr_building:
				address_to_update.building = paddr_building
			if paddr_floor:
				address_to_update.floor = paddr_floor
			if paddr_number:
				address_to_update.number = paddr_number
			if pzip_code:
				address_to_update.zip_code = pzip_code
			address_to_update.save()
		instance.save()
		crud_logger_info.info(
			f"object: property; stage: serialization; action_type: update; "
			f"user_id: {self.context['request'].user.id}; property_id: {instance.id}; "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")
		return instance


class BulkFileUploadSerializer(serializers.ModelSerializer):
	images = serializers.ListField(child=serializers.ImageField(allow_empty_file=True), max_length=6, required=True)

	class Meta:
		model = PremisesImages
		fields = (
			'id',
			'premises',
			'images',
			'uploaded_at',
			'is_main')
		read_only_fields = ['premises', 'id']

	def is_valid(self, raise_exception=False):
		ret = super(BulkFileUploadSerializer, self).is_valid(False)
		if self._errors:
			images_logger.info(
				f"object: image; stage: serialization; action_type: create; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['premises_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; status: NOT OK; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def create(self, validated_data):
		images = validated_data.get('images', None)
		if images:
			premises_image_instance = [
				PremisesImages(premises_id=self.context['premises_id'], image=image, is_main=False)
				for image in images]
			premises_image_instance[0].is_main = True
			PremisesImages.objects.bulk_create(premises_image_instance)
		images_logger.info(
			f"object: image; stage: serialization; action_type: create; user_id: {self.context['request'].user.id}; property_id: {self.context['premises_id']}; "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")
		return PremisesImages.objects.filter(premises_id=self.context['premises_id'])
