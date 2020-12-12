from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import serializers

from userAccount.serializers import ProfileListSerializer, ProfileSerializer
from .models import Property, PremisesAddresses, PremisesImages, Ownership
from userAccount.models import Profile
from .validators import validate_price
#
#


class FilteringNotMainImagesListSerializer(serializers.ListSerializer):

	def to_representation(self, data):
		data = data.filter(is_main=False)
		return super(FilteringNotMainImagesListSerializer, self).to_representation(data)


class PropertyOwnershipListSerializer(serializers.ModelSerializer):
	class Meta:
		model = Ownership
		fields = (
			'owner',
			'is_initial_owner',
			'permission_level',
			'granted_at'
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
	paddr_country = serializers.CharField(max_length=100, required=True)
	paddr_city = serializers.CharField(max_length=100, required=True)
	paddr_street_1 = serializers.CharField(max_length=100, required=True)
	paddr_street_2 = serializers.CharField(max_length=100, required=True)
	paddr_building = serializers.CharField(max_length=20, required=True)
	paddr_floor = serializers.CharField(max_length=20, required=True)
	paddr_number = serializers.CharField(max_length=30, required=True)
	pzip_code = serializers.CharField(max_length=10, required=True)

	class Meta:
		model = PremisesAddresses
		fields = (
			'paddr_country',
			'paddr_city',
			'paddr_street_1',
			'paddr_street_2',
			'paddr_building',
			'paddr_floor',
			'paddr_number',
			'pzip_code',
		)


class PropertyListSerializer(serializers.ModelSerializer):
	property_address = PropertyAddressesSerializer(many=True, read_only=True)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	main_image = serializers.SerializerMethodField('get_main_image', read_only=True)
	id = serializers.IntegerField(read_only=True)
	property_type_id = serializers.IntegerField(read_only=True)

	class Meta:
		model = Property

		fields = (
			'id',
			'creator_id',
			'title',
			'body',
			'price',
			'active',
			'property_type_id',
			'main_image',
			'property_address',
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
	property_address = PropertyAddressesSerializer(many=True, read_only=True)
	property_images = PropertyImagesSerializer(many=True, read_only=True)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	owners = PropertyOwnershipListSerializer(many=True, read_only=True)
	main_image = serializers.SerializerMethodField('get_main_image')
	id = serializers.IntegerField()
	property_type_id = serializers.IntegerField(read_only=True)

	class Meta:
		model = Property

		fields = (
			'id',
			'title',
			'body',
			'price',
			'creator_id',
			'active',
			'property_type_id',
			'main_image',
			'owners',
			'property_address',
			'property_images',
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
	property_address = PropertyAddressesSerializer(many=True, required=True)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	property_type_id = serializers.IntegerField(required=True)

	class Meta:
		model = Property

		fields = [
			'id',
			'creator_id',
			"title",
			"body",
			"property_type_id",
			"price",
			"active",
			"property_address",
			'created_at',
			'updated_at',
		]
		read_only_fields = ['creator', 'id']

	def create(self, validated_data):
		property_addresses = validated_data.pop('property_address')

		title = validated_data["title"]
		body = validated_data["body"]
		price = validated_data["price"]
		visibility = validated_data.get("visibility", None)

		property_type = validated_data["property_type_id"]
		active = validated_data.get("active", None)
		if len(property_addresses) > 1:
			raise serializers.ValidationError({"property_address": "Check your input again."})
		if active is None:
			active = True
		if visibility is None:
			visibility = 100
		property_to_create = Property.objects.create(
			author=self.context['request'].user,
			title=title, body=body, price=price, active=active, property_type_id=property_type, visibility=visibility)
		for i in property_addresses:
			PremisesAddresses.objects.create(**i, premises=property_to_create)
		return property_to_create


class PropertyUpdateSerializer(serializers.ModelSerializer):
	property_address = PropertyAddressesSerializer(many=True, required=False)
	property_images = PropertyImagesSerializer(many=True, required=False)
	creator_id = serializers.IntegerField(read_only=True, source='author.id')
	owners = PropertyOwnershipListSerializer(many=True, required=False)
	main_image = serializers.SerializerMethodField('get_main_image')
	id = serializers.IntegerField(read_only=True)
	property_type_id = serializers.IntegerField(required=False)
	visibility = serializers.IntegerField(required=False)

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
			'property_type_id',
			'main_image',
			'owners',
			'property_address',
			'property_images',
			'visibility',
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
			if len(address_data) > 1:
				raise serializers.ValidationError(
					{
						"property_address": "Check your input again."
					}
				)
			else:
				address_to_update = PremisesAddresses.objects.get(premises_id=instance.id)
				paddr_country = address_data[0].get('paddr_country', None)
				paddr_city = address_data[0].get('paddr_city', None)
				paddr_street_1 = address_data[0].get('paddr_street_1', None)
				paddr_street_2 = address_data[0].get('paddr_street_2', None)
				paddr_building = address_data[0].get('paddr_building', None)
				paddr_floor = address_data[0].get('paddr_floor', None)
				paddr_number = address_data[0].get('paddr_number', None)
				pzip_code = address_data[0].get('pzip_code', None)
				if paddr_country:
					address_to_update.paddr_country = paddr_country
				if paddr_city:
					address_to_update.paddr_city = paddr_city
				if paddr_street_1:
					address_to_update.paddr_street_1 = paddr_street_1
				if paddr_street_2:
					address_to_update.paddr_street_2 = paddr_street_2
				if paddr_building:
					address_to_update.paddr_building = paddr_building
				if paddr_floor:
					address_to_update.paddr_floor = paddr_floor
				if paddr_number:
					address_to_update.paddr_number = paddr_number
				if pzip_code:
					address_to_update.pzip_code = pzip_code
				address_to_update.save()
		instance.save()
		return instance


class BookingCreateSerializer(serializers.ModelSerializer):
	# TODO: fill in
	pass


class BookingUpdateSerializer(serializers.ModelSerializer):
	# TODO: fill in
	pass


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
