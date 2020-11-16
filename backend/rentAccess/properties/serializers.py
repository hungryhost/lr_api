from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Property, Profile
from .validators import validate_price
#
#


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
		fields = ('author_id', 'id', 'title', 'body', 'price', 'active', 'image',)
		read_only_fields = ['author_id', 'id']


class PropertyCreateSerializer(serializers.ModelSerializer):
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
	image = serializers.CharField(required=False)

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
			"image"
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
		image = validated_data.get("image", None)
		if image is None:
			image = "/media/defaults/property_default.png"
		if active is None:
			active = True
		property_to_create = Property(
			author=Profile.objects.get(user=self.context['request'].user),
			title=title, body=body, price=price, active=active, image=image)
		property_to_create.save()
		return property_to_create


class PropertyUpdateSerializer(serializers.ModelSerializer):
	"""
	Serializer class for updating a property.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	price = serializers.IntegerField(required=True, validators=[validate_price])

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
			"image"
		]
		read_only_fields = ['author_id', 'id']

	def update(self, instance, validated_data):
		"""
		Explicitly created method. Seed docs on serializers.
		:param validated_data
		:return:
		"""
		instance.title = validated_data["title"]
		instance.body = validated_data["body"]
		instance.price = validated_data["price"]
		active = validated_data.get("active", None)
		image = validated_data.get("image", None)
		if active is not None:
			instance.active = validated_data["active"]
		if image is not None:
			instance.image = validated_data["image"]
		instance.save()
		return instance






