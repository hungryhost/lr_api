from django.http import Http404
from rest_framework import serializers
from register.models import Lock
from properties.models import LockWithProperty
import datetime
from userAccount.serializers import UserSerializer
from .models import LockMessage, LockCatalogInfo, LockAvailabilityStorage, LockCatalogImages


class LockImageSerializer(serializers.ModelSerializer):
	class Meta:
		model = LockCatalogImages
		fields = '__all__'
		#read_only_fields = [fields]


class LockAvailabilitySerializer(serializers.ModelSerializer):
	class Meta:
		model = LockAvailabilityStorage
		fields = [
			'quantity'
		]
		#read_only_fields = [fields]


class LockInfoLightSerializer(serializers.ModelSerializer):
	main_image = serializers.SerializerMethodField('get_main_image')

	class Meta:
		model = LockCatalogInfo
		fields = [
			'name',
			'description',
			'price',
			'delivery',
			'main_image',
			'installation_included',
			'is_available',
			'created_at',
			'updated_at'
		]

	def get_main_image(self, obj):
		try:
			images = obj.catalog_images.all()
			main = None
			for image in images:
				if image.is_main is True:
					main = image
			return self.context.get('request').build_absolute_uri(
				main.image.url)
		except Exception:
			return ""


class LockInfoSerializer(serializers.ModelSerializer):
	availability = serializers.SerializerMethodField('get_lock_availability')
	catalog_images = LockImageSerializer(many=True, read_only=True)
	main_image = serializers.SerializerMethodField('get_main_image')

	class Meta:
		model = LockCatalogInfo
		fields = [
			'name',
			'description',
			'price',
			'delivery',
			'installation_included',
			'is_available',
			'availability',
			'main_image',
			'catalog_images',
			'created_at',
			'updated_at'
		]
		#read_only_fields = [fields]

	def get_lock_availability(self, obj):
		serializer = LockAvailabilitySerializer(
			obj.lock_availability,
			many=True
		)
		return serializer.data

	def get_main_image(self, obj):
		try:
			images = obj.catalog_images.all()
			main = None
			for image in images:
				if image.is_main is True:
					main = image
			return self.context.get('request').build_absolute_uri(
				main.image.url)
		except Exception:
			return ""


class LockMessageCreateSerializer(serializers.ModelSerializer):
	selected_lock_id = serializers.IntegerField(allow_null=True, required=False)
	quantity = serializers.IntegerField(min_value=1, max_value=500, allow_null=False, required=True)

	class Meta:
		model = LockMessage
		fields = [
			'email',
			'fio',
			'selected_lock_id',
			'phone',
			'comment',
			'status',
			'company',
			'quantity',
			'final_price'
		]
		read_only_fields = [
			'final_price',
			'status'
		]

	def to_representation(self, instance):

		selected_lock = LockInfoLightSerializer(
			instance.selected_lock,
			many=False, read_only=True

		)
		representation = super().to_representation(instance)
		if instance.selected_lock:
			representation['selected_lock'] = selected_lock.data
		else:
			representation['selected_lock'] = None
		return representation

	def create(self, validated_data):
		selected_lock = validated_data.pop('selected_lock_id', None)

		lock_to_db = None
		if selected_lock:
			try:
				lock = LockCatalogInfo.objects.get(pk=selected_lock)
			except LockCatalogInfo.DoesNotExist:
				lock = None
			if lock:
				try:
					availability = LockAvailabilityStorage.objects.filter(
						lock_info=lock
					).latest('created_at')
				except LockAvailabilityStorage.DoesNotExist:
					availability = None

				if availability and availability.quantity > 0 and lock.is_available:
					lock_to_db = lock
					validated_data['final_price'] = lock.price * validated_data['quantity']

		message = LockMessage(
			**validated_data,
			selected_lock=lock_to_db,
			status='WAIT'
		)
		message.save()
		return message


class LockMessageListSerializer(serializers.ModelSerializer):
	selected_lock = LockInfoLightSerializer(many=False, read_only=True)
	selected_lock_id = serializers.SerializerMethodField('get_selected_lock_id')

	class Meta:
		model = LockMessage
		fields = [
			'id',
			'email',
			'fio',
			'selected_lock_id',
			'selected_lock',
			'phone',
			'status',
			'comment',
			'company',
			'quantity',
			'final_price'
		]

	def get_selected_lock_id(self, obj):
		selected_lock = obj.selected_lock
		if selected_lock:
			return selected_lock.id
		return None
