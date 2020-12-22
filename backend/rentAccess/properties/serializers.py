from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import serializers

from userAccount.serializers import ProfileListSerializer, ProfileSerializer
from .models import Property, PremisesAddresses, PremisesImages, Ownership, Bookings
from userAccount.models import Profile
from .validators import validate_price
#
#


class FilteringNotMainImagesListSerializer(serializers.ListSerializer):

	def to_representation(self, data):
		data = data.filter(is_main=False)
		return super(FilteringNotMainImagesListSerializer, self).to_representation(data)


class PropertyOwnershipListSerializer(serializers.ModelSerializer):
	email = serializers.CharField(read_only=True, source='user.email')
	first_name = serializers.CharField(source='user.first_name', read_only=True)
	last_name = serializers.CharField(source='user.last_name', read_only=True)

	patronymic = serializers.CharField(max_length=50, source='user.profile.patronymic',
									read_only=True)

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


class PropertyOwnershipAddSerializer(serializers.ModelSerializer):
	# TODO: fill in
	pass


class PropertyOwnershipUpdateSerializer(serializers.ModelSerializer):
	# TODO: fill in
	pass


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
	city = serializers.CharField(max_length=100, required=True)
	street_1 = serializers.CharField(max_length=100, required=True)
	street_2 = serializers.CharField(max_length=100, required=True)
	building = serializers.CharField(max_length=20, required=True)
	floor = serializers.CharField(max_length=20, required=True)
	number = serializers.CharField(max_length=30, required=True)
	zip_code = serializers.CharField(max_length=10, required=True)

	class Meta:
		model = PremisesAddresses
		fields = (
			'country',
			'city',
			'street_1',
			'street_2',
			'building',
			'floor',
			'number',
			'zip_code',
			'directions_description',
		)


class PropertyAddressesListSerializer(serializers.ModelSerializer):
	class Meta:
		model = PremisesAddresses
		fields = (
			'country',
			'city',
			'street_1',
			'street_2',
			'building',
			'floor',
			'number',
			'zip_code',
			'directions_description',
		)


class PropertyListSerializer(serializers.ModelSerializer):
	property_address = PropertyAddressesSerializer(many=False, read_only=True)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	main_image = serializers.SerializerMethodField('get_main_image', read_only=True)
	id = serializers.IntegerField(read_only=True)
	client_greeting_message = serializers.CharField(required=False)

	class Meta:
		model = Property

		fields = (
			'id',
			'creator_id',
			'title',
			'body',
			'price',
			'active',
			'property_type',
			'main_image',
			'property_address',
			'created_at',
			'updated_at',
			'client_greeting_message'

		)

		read_only_fields = ['id']

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception as e:
			return ""

	def get_owners_url(self, obj):
		try:
			return self.context.get('request').build_absolute_uri(
				reverse('properties:property-list')) + '{id}/owners/'.format(id=obj.pk)
		except Exception as e:
			return str(e)


class PropertySerializer(serializers.ModelSerializer):
	"""
	Serializer class for general purposes.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	property_address = PropertyAddressesSerializer(many=False, read_only=True)
	property_images = PropertyImagesSerializer(many=True, read_only=True)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	owners = PropertyOwnershipListSerializer(many=True, read_only=True)
	main_image = serializers.SerializerMethodField('get_main_image')
	id = serializers.IntegerField()

	class Meta:
		model = Property

		fields = (
			'id',
			'title',
			'body',
			'price',
			'creator_id',
			'active',
			'property_type',
			'main_image',
			'owners',
			'property_address',
			'property_images',
			'client_greeting_message',
			'created_at',
			'updated_at',

		)
		read_only_fields = ['id']

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception as e:
			return ""

	def get_owners_url(self, obj):
		try:
			return self.context.get('request').build_absolute_uri(reverse('properties:property-list')) + '{id}/owners/'.format(id=obj.pk)
		except Exception as e:
			return str(e)


class PropertyCreateSerializer(serializers.ModelSerializer):
	title = serializers.CharField(required=True)
	body = serializers.CharField(required=True)
	price = serializers.IntegerField(required=True, validators=[validate_price])
	active = serializers.BooleanField(required=False)
	property_address = PropertyAddressesSerializer(many=False, required=True)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	client_greeting_message = serializers.CharField(required=False)
	main_image = serializers.SerializerMethodField('get_main_image', read_only=True)

	class Meta:
		model = Property

		fields = [
			'id',
			'creator_id',
			'title',
			'body',
			'price',
			'active',
			'property_type',
			'main_image',
			'property_address',
			'client_greeting_message',
			'created_at',
			'updated_at',
		]
		read_only_fields = ['creator', 'id']

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception as e:
			return ""

	def create(self, validated_data):
		property_addresses = validated_data.pop('property_address')

		title = validated_data["title"]
		body = validated_data["body"]
		price = validated_data["price"]
		visibility = validated_data.get("visibility", None)

		property_type = validated_data["property_type"]
		active = validated_data.get("active", None)

		if active is None:
			active = True
		if visibility is None:
			visibility = 100
		property_to_create = Property.objects.create(
			author=self.context['request'].user,
			title=title, body=body, price=price, active=active, property_type=property_type, visibility=visibility)

		PremisesAddresses.objects.create(premises=property_to_create, **property_addresses)

		return property_to_create


class PropertyUpdateSerializer(serializers.ModelSerializer):
	property_address = PropertyAddressesSerializer(many=False, required=False)
	property_images = PropertyImagesSerializer(many=True, required=False)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	owners = PropertyOwnershipListSerializer(many=True, required=False)
	main_image = serializers.SerializerMethodField('get_main_image')
	id = serializers.IntegerField(read_only=True)
	visibility = serializers.IntegerField(required=False)
	client_greeting_message = serializers.CharField(required=False)

	class Meta:
		model = Property
		author_id = serializers.Field(source='author')
		fields = (
			'id',
			'title',
			'body',
			'price',
			'creator_id',
			'active',
			'property_type',
			'main_image',
			'owners',
			'property_address',
			'property_images',
			'visibility',
			'client_greeting_message',
			'created_at',
			'updated_at',


		)
		read_only_fields = ['creator_id', 'id']

	def get_main_image(self, obj):
		try:
			image_object = PremisesImages.objects.get(premises=obj, is_main=True)
			return self.context['request'].build_absolute_uri(image_object.image.url)
		except Exception as e:
			return ""

	def to_representation(self, instance):

		representation = super(PropertyUpdateSerializer, self).to_representation(instance)
		representation.pop('visibility')
		return representation

	def update(self, instance, validated_data):
		"""
		Explicitly created method. Seed docs on serializers.
		:param instance
		:param validated_data
		:return: instance
		"""
		address_data = validated_data.pop("property_address", None)
		title = validated_data.get("title", None)
		body = validated_data.get("body", None)
		price = validated_data.get("price", None)
		active = validated_data.get("active", None)
		visibility = validated_data.get("visibility", None)
		property_type_id = validated_data.get("property_type_id", None)

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

		if address_data:
			address_to_update = PremisesAddresses.objects.get(premises_id=instance.id)
			country = address_data.get('country', None)
			paddr_city = address_data.get('city', None)
			paddr_street_1 = address_data.get('street_1', None)
			paddr_street_2 = address_data.get('street_2', None)
			paddr_building = address_data.get('building', None)
			paddr_floor = address_data.get('floor', None)
			paddr_number = address_data.get('number', None)
			pzip_code = address_data.get('zip_code', None)
			if country:
				address_to_update.country = country
			if paddr_city:
				address_to_update.city = paddr_city
			if paddr_street_1:
				address_to_update.street_1 = paddr_street_1
			if paddr_street_2:
				address_to_update.street_2 = paddr_street_2
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
		return instance


class BookingsSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(required=True)
	booked_until = serializers.DateTimeField(required=True)
	client_email = serializers.EmailField(required=True)

	class Meta:
		model = Bookings
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'booked_by',
			'created_at',
			'updated_at',
			'id',
			'status'
		]

	def validate(self, attrs):
		if (attrs["booked_from"] >= attrs["booked_until"]) \
				or (attrs["booked_until"] <= attrs["booked_from"]):
			raise serializers.ValidationError({
				"dates": "Dates are not valid",
			})
		return super(BookingsSerializer, self).validate(attrs)

	def create(self, validated_data):
		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		client_email = validated_data.get("client_email")
		created_booking = Bookings(
			number_of_clients=number_of_clients,
			booked_from=booked_from,
			booked_until=booked_until,
			client_email=client_email,
			booked_property_id=self.context["property_id"],
			booked_by=self.context["request"].user
		)
		if Ownership.objects.filter(premises_id=self.context["property_id"], user=self.context["request"].user).exists():
			created_booking.status = "ACCEPTED"
		created_booking.save()
		return created_booking


class BookingsListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Bookings
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at'
		)


class BookingUpdateAdminAndCreatorSerializer(serializers.ModelSerializer):
	status = serializers.CharField(required=False)
	number_of_clients = serializers.IntegerField(required=False, max_value=100)
	booked_from = serializers.DateTimeField(required=False)
	booked_until = serializers.DateTimeField(required=False)

	class Meta:
		model = PremisesImages
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'client_email',
			'booked_by',
			'created_at',
			'updated_at']

	def update(self, instance, validated_data):
		status = validated_data.get("status", None)
		number_of_clients = validated_data.get("number_of_clients", None)
		booked_from = validated_data.get("booked_from", None)
		booked_until = validated_data.get("booked_until", None)
		if status:
			instance.status = status
		if number_of_clients:
			instance.number_of_clients = number_of_clients
		if booked_from:
			instance.booked_from = booked_from
		if booked_until:
			instance.booked_from = booked_until

		instance.save()
		return instance


class BookingUpdateAdminNotCreatorSerializer(serializers.ModelSerializer):
	status = serializers.CharField(required=False)

	class Meta:
		model = PremisesImages
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at']

	def update(self, instance, validated_data):
		status = validated_data.get("status", None)
		if status:
			instance.status = status
		instance.save()
		return instance


class BookingUpdateClientSerializer(serializers.ModelSerializer):
	number_of_clients = serializers.IntegerField(required=False, max_value=100)
	booked_from = serializers.DateTimeField(required=False)
	booked_until = serializers.DateTimeField(required=False)

	class Meta:
		model = PremisesImages
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'booked_from',
			'status',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at']

	def update(self, instance, validated_data):
		number_of_clients = validated_data.get("number_of_clients", None)
		booked_from = validated_data.get("booked_from", None)
		booked_until = validated_data.get("booked_until", None)
		if number_of_clients:
			instance.number_of_clients = number_of_clients
		if booked_from:
			instance.booked_from = booked_from
		if booked_until:
			instance.booked_from = booked_until

		instance.save()
		return instance


class BulkFileUploadSerializer(serializers.ModelSerializer):
	images = serializers.ListField(child=serializers.ImageField(allow_empty_file=True), max_length=6, required=True)

	class Meta:
		model = PremisesImages
		fields = ('premises',
				'images',
				'uploaded_at',
				'is_main')
		read_only_fields = ['premises']

	def create(self, validated_data):
		images = validated_data.get('images', None)
		if images:
			premises_image_instance = [PremisesImages(premises_id=self.context['premises_id'], image=image, is_main=False)
									for image in images]
			premises_image_instance[0].is_main = True
			PremisesImages.objects.bulk_create(premises_image_instance)
		return PremisesImages.objects.filter(premises_id=self.context['premises_id'])
