from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import serializers, status

import logging

from properties.logger_helpers import get_client_ip
from properties.models import Property, Ownership
from properties.serializers import PropertyListSerializer
from .models import Bookings
User = get_user_model()
crud_logger_info = logging.getLogger('rentAccess.properties.crud.info')
owners_logger = logging.getLogger('rentAccess.properties.owners.info')
bookings_logger = logging.getLogger('rentAccess.properties.bookings.info')
images_logger = logging.getLogger('rentAccess.properties.images.info')


class BookingsSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
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

	def is_valid(self, raise_exception=False):
		ret = super(BookingsSerializer, self).is_valid(False)
		if self._errors:
			bookings_logger.info(
				f"object: booking; stage: serialization; action_type: create; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; status: NOT OK; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def validate(self, attrs):
		if attrs["booked_from"] > attrs["booked_until"]:
			raise serializers.ValidationError({
				"dates": "Dates are not valid",
			})

		if self.context["request"].user.email == attrs["client_email"]:
			raise serializers.ValidationError({
				"Error": "Cannot book property you own for yourself.",
			})
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__lte=attrs["booked_from"]) & Q(booked_until__gte=attrs["booked_from"]), query_1.connector)
		query_1.add(Q(booked_from__lt=attrs["booked_until"]) & Q(booked_until__gte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_from__gte=attrs["booked_from"]) & Q(booked_from__lte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=attrs["booked_until"]) | Q(booked_until=attrs["booked_from"]), query_2.connector)
		queryset = Bookings.objects.filter(query_1).exclude(query_2)

		if queryset.exists():
			raise serializers.ValidationError({
				"dates": "Cannot book with these dates",
			}, code=status.HTTP_409_CONFLICT)
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
		if Ownership.objects.filter(premises_id=self.context["property_id"],
									user=self.context["request"].user).exists() or (not
				Property.objects.get(id=self.context["property_id"]).requires_additional_confirmation
		):
			created_booking.status = "ACCEPTED"
		created_booking.save()
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
			f"booking_id: {created_booking.id}; ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return created_booking


class BookingCreateFromClientSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)

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

	def is_valid(self, raise_exception=False):
		ret = super(BookingCreateFromClientSerializer, self).is_valid(False)
		if self._errors:
			bookings_logger.info(
				f"object: booking; stage: serialization; action_type: create; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; status: NOT OK; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def validate(self, attrs):
		if attrs["booked_from"] > attrs["booked_until"]:
			raise serializers.ValidationError({
				"dates": "Dates are not valid",
			})

		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__lte=attrs["booked_from"]) & Q(booked_until__gte=attrs["booked_from"]),
					query_1.connector)
		query_1.add(Q(booked_from__lt=attrs["booked_until"]) & Q(booked_until__gte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_from__gte=attrs["booked_from"]) & Q(booked_from__lte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=attrs["booked_until"]) | Q(booked_until=attrs["booked_from"]), query_2.connector)
		queryset = Bookings.objects.filter(query_1).exclude(query_2)

		if queryset.exists():
			raise serializers.ValidationError({
				"dates": "Cannot book with these dates",
			}, code=status.HTTP_409_CONFLICT)
		return super(BookingCreateFromClientSerializer, self).validate(attrs)

	def create(self, validated_data):
		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		created_booking = Bookings(
			number_of_clients=number_of_clients,
			booked_from=booked_from,
			booked_until=booked_until,
			client_email=self.context["request"].user.email,
			booked_property_id=self.context["property_id"],
			booked_by=self.context["request"].user
		)
		if not Property.objects.get(id=self.context["property_id"]).requires_additional_confirmation:
			created_booking.status = "ACCEPTED"
		created_booking.save()
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: "
			f"{self.context['property_id']}; booking_id: {created_booking.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return created_booking


class BookingsListSerializer(serializers.ModelSerializer):
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)

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
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)

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
			'id',
			'booked_property',
			'client_email',
			'booked_by',
			'created_at',
			'updated_at']

	def is_valid(self, raise_exception=False):
		ret = super(BookingUpdateAdminAndCreatorSerializer, self).is_valid(False)
		if self._errors:
			bookings_logger.info(
				f"object: booking; stage: serialization; action_type: create; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; status: NOT OK; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def validate(self, attrs):
		if attrs["booked_from"] > attrs["booked_until"]:
			raise serializers.ValidationError({
				"dates": "Dates are not valid",
			})
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__lte=attrs["booked_from"]) & Q(booked_until__gte=attrs["booked_from"]),
					query_1.connector)
		query_1.add(Q(booked_from__lt=attrs["booked_until"]) & Q(booked_until__gte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_from__gte=attrs["booked_from"]) & Q(booked_from__lte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=attrs["booked_until"]) | Q(booked_until=attrs["booked_from"]), query_2.connector)
		queryset = Bookings.objects.filter(query_1).exclude(query_2)

		if queryset.exists():
			raise serializers.ValidationError({
				"dates": "Cannot book with these dates",
			}, code=status.HTTP_409_CONFLICT)
		if (not attrs.get("booked_from") and attrs.get("booked_until")) or (
				attrs.get("booked_from") and not attrs.get("booked_until")
		):
			raise serializers.ValidationError({
				"dates": "Provide both dates",
			})
		return super(BookingUpdateAdminAndCreatorSerializer, self).validate(attrs)

	def update(self, instance, validated_data):
		status_ = validated_data.get("status", None)
		number_of_clients = validated_data.get("number_of_clients", None)
		booked_from = validated_data.get("booked_from", None)
		booked_until = validated_data.get("booked_until", None)
		if status:
			instance.status = status_
		if number_of_clients:
			instance.number_of_clients = number_of_clients
		if booked_from:
			instance.booked_from = booked_from
		if booked_until:
			instance.booked_until = booked_until

		instance.save()
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; booking_id: {instance.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return instance


class BookingUpdateAdminNotCreatorSerializer(serializers.ModelSerializer):
	status = serializers.CharField(required=True)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", read_only=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", read_only=True)

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
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at']

	def is_valid(self, raise_exception=False):
		ret = super(BookingUpdateAdminNotCreatorSerializer, self).is_valid(False)
		if self._errors:
			bookings_logger.info(
				f"object: booking; stage: serialization; action_type: create; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; status: NOT OK; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def update(self, instance, validated_data):
		status = validated_data.get("status", None)
		if status:
			instance.status = status
		instance.save()
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; booking_id: {instance.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return instance


class BookingUpdateClientSerializer(serializers.ModelSerializer):
	number_of_clients = serializers.IntegerField(required=False, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)

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

	def is_valid(self, raise_exception=False):
		ret = super(BookingUpdateClientSerializer, self).is_valid(False)
		if self._errors:
			bookings_logger.info(
				f"object: booking; stage: serialization; action_type: create; "
				f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; "
				f"ip_addr: {get_client_ip(self.context['request'])}; status: NOT OK; serialization failed;")
			if raise_exception:
				raise serializers.ValidationError(self.errors)
		return ret

	def validate(self, attrs):
		if attrs.get("booked_from") and attrs.get("booked_until"):
			if (attrs["booked_from"] >= attrs["booked_until"]) \
					or (attrs["booked_until"] <= attrs["booked_from"]):
				raise serializers.ValidationError({
					"dates": "Dates are not valid",
				})
			query_1 = Q()
			# query_1.add(Q(booked_property_id=1), Q.AND)
			# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
			query_1.add(Q(booked_from__lte=attrs["booked_from"]) & Q(booked_until__gte=attrs["booked_from"]),
						query_1.connector)
			query_1.add(Q(booked_from__lt=attrs["booked_until"]) & Q(booked_until__gte=attrs["booked_until"]), Q.OR)
			query_1.add(Q(booked_from__gte=attrs["booked_from"]) & Q(booked_from__lte=attrs["booked_until"]), Q.OR)
			query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
			query_2 = Q()
			query_2.add(Q(booked_from=attrs["booked_until"]) | Q(booked_until=attrs["booked_from"]), query_2.connector)
			queryset = Bookings.objects.filter(query_1).exclude(query_2)

			if queryset.exists():
				raise serializers.ValidationError({
					"dates": "Cannot book with these dates",
				}, code=status.HTTP_409_CONFLICT)
		if (not attrs.get("booked_from") and attrs.get("booked_until")) or (
				attrs.get("booked_from") and not attrs.get("booked_until")
		):
			raise serializers.ValidationError({
				"dates": "Provide both dates",
			})
		return super(BookingUpdateClientSerializer, self).validate(attrs)

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
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; booking_id: {instance.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return instance

