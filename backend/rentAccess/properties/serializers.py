from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Property, Profile
from .validators import validate_price
#
#
# TODO: add main image and additional images available


class PropertySerializer(serializers.ModelSerializer):
	"""
	Serializer class for general purposes.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	class Meta:
		model = Property
		author_id = serializers.Field(source='author')
		fields = ('author_id', 'id', 'title', 'body', 'price', 'active',)
		read_only_fields = ['author_id', 'id']


class PropertyCreateUpdateSerializer(serializers.ModelSerializer):
	"""
	Serializer class for creating a property.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	title = serializers.CharField(required=True)
	body = serializers.CharField(required=True)
	price = serializers.IntegerField(required=True, validators=[validate_price])
	active = serializers.BooleanField(required=False)

	class Meta:
		model = Property
		author_id = serializers.Field(source='author')
		fields = [
			'author_id',
			'id',
			"title",
			"body",
			"price",
			"active",
		]
		read_only_fields = ['author_id', 'id']

	def create(self, validated_data):
		"""
		Explicitly created method. Seed docs on serializers.
		:param validated_data
		:return:
		"""
		title = validated_data["title"]
		body = validated_data["body"]
		price = validated_data["price"]

		active = validated_data.get("active", None)

		if active is None:
			active = True
		property_to_create = Property(
			author=Profile.objects.get(user=self.context['request'].user),
			title=title, body=body, price=price, active=active)
		property_to_create.save()
		return property_to_create


class PropertyUpdateSerializer(serializers.ModelSerializer):
	title = serializers.CharField(required=False)
	body = serializers.CharField(required=False)
	price = serializers.IntegerField(required=False, validators=[validate_price])
	active = serializers.BooleanField(required=False)

	class Meta:
		model = Property
		author_id = serializers.Field(source='author')
		fields = [
			'author_id',
			'id',
			"title",
			"body",
			"price",
			"active",
		]
		read_only_fields = ['author_id', 'id']

	def update(self, instance, validated_data):
		"""
		Explicitly created method. Seed docs on serializers.
		:param instance
		:param validated_data
		:return: instance
		"""
		title = validated_data.get("title", None)
		body = validated_data.get("body", None)
		price = validated_data.get("price", None)
		active = validated_data.get("active", None)


		if title is not None:
			instance.title = validated_data["title"]
		if body is not None:
			instance.body = validated_data["body"]
		if price is not None:
			instance.price = validated_data["price"]
		if active is not None:
			instance.active = validated_data["active"]

		instance.save()
		return instance





