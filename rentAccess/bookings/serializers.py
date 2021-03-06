from datetime import datetime
from .timezone_utils import utc_to_aware
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers, status
import logging
from properties.availability_utils import available_days_from_db, available_hours_from_db, \
	decompose_incoming_booking
from properties.logger_helpers import get_client_ip
from properties.models import Property, Ownership
from properties.serializers import PropertyListSerializer
from .models import Booking

User = get_user_model()
crud_logger_info = logging.getLogger('rentAccess.properties.crud.info')
owners_logger = logging.getLogger('rentAccess.properties.owners.info')
bookings_logger = logging.getLogger('rentAccess.properties.bookings.info')
images_logger = logging.getLogger('rentAccess.properties.images.info')


class DailyBookingCreateFromOwnerSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100, min_value=1)
	booked_from = serializers.DateTimeField(input_formats=["%Y-%m-%d"], required=True)
	booked_until = serializers.DateTimeField(input_formats=["%Y-%m-%d"], required=True)
	client_email = serializers.EmailField(required=True)
	timezone = serializers.SerializerMethodField('get_timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'price',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
			'booked_by',
			'created_at',
			'updated_at',
			'id',
			'price',
			'status'
		]

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		property_to_book = self.context['property']
		timezone = property_to_book.property_address.city.city.timezone
		booked_from_with_time = utc_to_aware(datetime.combine(
				instance.booked_from,
				property_to_book.availability.available_from),
			timezone)
		booked_until_with_tile = utc_to_aware(datetime.combine(
				instance.booked_until, property_to_book.availability.available_until),
			timezone)

		representation["booked_from"] = booked_from_with_time.strftime("%Y-%m-%dT%H:%M%z")
		representation["booked_until"] = booked_until_with_tile.strftime("%Y-%m-%dT%H:%M%z")
		return representation

	def validate(self, attrs):
		if attrs["booked_from"] >= attrs["booked_until"]:
			raise serializers.ValidationError({
				'dates': "Dates are not valid"
			})

		if self.context["request"].user.email == attrs["client_email"]:
			raise serializers.ValidationError({
				"client_email": "Cannot book property you own for yourself.",
			})
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__date__lte=attrs["booked_from"]) & Q(booked_until__date__gte=attrs["booked_from"]),
			query_1.connector)
		query_1.add(Q(booked_from__date__lt=attrs["booked_until"]) & Q(booked_until__date__gte=attrs["booked_until"]),
			Q.OR)
		query_1.add(Q(booked_from__date__gte=attrs["booked_from"]) & Q(booked_from__date__lte=attrs["booked_until"]),
			Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from__date=attrs["booked_until"]) | Q(booked_until__date=attrs["booked_from"]),
			query_2.connector)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			raise serializers.ValidationError({
				'dates': "Cannot book with these dates"
			})

		return super(DailyBookingCreateFromOwnerSerializer, self).validate(attrs)

	def get_timezone(self, obj):
		return self.context['property'].property_address.city.city.timezone

	def create(self, validated_data):

		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		client_email = validated_data.get("client_email")

		property_to_book = self.context['property']
		timezone = property_to_book.property_address.city.city.timezone
		booked_from_with_time = utc_to_aware(
			datetime.combine(booked_from, property_to_book.availability.available_from),
			timezone
		)
		booked_until_with_tile = utc_to_aware(
			datetime.combine(booked_until, property_to_book.availability.available_until),
			timezone
		)

		if property_to_book.price:
			delta = booked_until - booked_from
			price = self.context['property'].price * delta.days
		else:
			price = None

		created_booking = Booking(
			number_of_clients=number_of_clients,
			booked_from=booked_from_with_time,
			booked_until=booked_until_with_tile,
			client_email=client_email,
			booked_property_id=self.context["property_id"],
			booked_by=self.context["request"].user,
			price=price
		)
		created_booking.status = "ACCEPTED"
		created_booking.save()
		return created_booking


class DailyBookingCreateFromClientSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(input_formats=["%Y-%m-%d"], format="%Y-%m-%d", required=True)
	booked_until = serializers.DateTimeField(input_formats=["%Y-%m-%d"], format="%Y-%m-%d", required=True)
	timezone = serializers.SerializerMethodField('get_timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'price',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
			'booked_by',
			'created_at',
			'updated_at',
			'id',
			'status',
			'price'
		]

	def get_timezone(self, obj):
		return self.context['property'].property_address.city.city.timezone

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		property_to_book = self.context['property']
		timezone = property_to_book.property_address.city.city.timezone
		booked_from_with_time = utc_to_aware(
			datetime.combine(
				instance.booked_from,
				property_to_book.availability.available_from),
			timezone
		)
		booked_until_with_tile = utc_to_aware(
			datetime.combine(
				instance.booked_until, property_to_book.availability.available_until),
			timezone
		)

		representation["booked_from"] = booked_from_with_time.strftime("%Y-%m-%dT%H:%M%z")
		representation["booked_until"] = booked_until_with_tile.strftime("%Y-%m-%dT%H:%M%z")
		return representation

	def validate(self, attrs):
		if attrs["booked_from"] >= attrs["booked_until"]:
			raise serializers.ValidationError({
				"dates": "Dates are not valid",
			})

		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__date__lte=attrs["booked_from"]) & Q(booked_until__date__gte=attrs["booked_from"]),
			query_1.connector)
		query_1.add(Q(booked_from__date__lt=attrs["booked_until"]) & Q(booked_until__date__gte=attrs["booked_until"]),
			Q.OR)
		query_1.add(Q(booked_from__date__gte=attrs["booked_from"]) & Q(booked_from__date__lte=attrs["booked_until"]),
			Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from__date=attrs["booked_until"]) | Q(booked_until__date=attrs["booked_from"]),
			query_2.connector)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			raise serializers.ValidationError(
				"Cannot book with these dates")

		return super(DailyBookingCreateFromClientSerializer, self).validate(attrs)

	def create(self, validated_data):
		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")

		property_to_book = self.context['property']
		timezone = property_to_book.property_address.city.city.timezone
		booked_from_with_time = utc_to_aware(
			datetime.combine(booked_from, property_to_book.availability.available_from),
			timezone
		)
		booked_until_with_tile = utc_to_aware(
			datetime.combine(booked_until, property_to_book.availability.available_until),
			timezone
		)
		if property_to_book.price:
			delta = booked_until.date() - booked_from.date()
			price = self.context['property'].price * delta.days
		else:
			price = None
		created_booking = Booking(
			number_of_clients=number_of_clients,
			booked_from=booked_from_with_time,
			booked_until=booked_until_with_tile,
			client_email=self.context["request"].user.email,
			booked_property_id=self.context["property_id"],
			booked_by=self.context["request"].user,
			price=price
		)
		if not property_to_book.requires_additional_confirmation:
			created_booking.status = "ACCEPTED"
		created_booking.save()
		return created_booking


class HourlyBookingCreateFromOwnerSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
	client_email = serializers.EmailField(required=True)
	timezone = serializers.SerializerMethodField('get_timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
			'booked_by',
			'created_at',
			'updated_at',
			'id',
			'status'
		]

	def get_timezone(self, obj):
		return self.context['property'].property_address.city.city.timezone

	def validate(self, attrs):
		if attrs["booked_from"] >= attrs["booked_until"]:
			raise serializers.ValidationError({
				'dates': "Dates are not valid"
			})

		if self.context["request"].user.email == attrs["client_email"]:
			raise serializers.ValidationError({
				"client_email": "Cannot book property you own for yourself.",
			})
		# we retrieve the property from context in order to reduce sql queries
		property_to_book = self.context['property']

		# dates are retrieved as datetime.datetime
		booked_from_dt = attrs["booked_from"]
		booked_until_dt = attrs["booked_until"]

		# we need to get available days from bd in order to check whether
		# we're booking on an available day
		days = available_days_from_db(property_to_book.availability.open_days)
		# here we check that
		if (booked_from_dt.weekday() not in days) or (booked_until_dt.weekday() not in days):
			raise serializers.ValidationError(
				"Property is not available at that day."
			)

		bookings = Booking.objects.all().filter(
			booked_property=property_to_book,
			booked_from__date=booked_from_dt.date(),
			booked_until__date=booked_until_dt.date()
		)

		timezone = property_to_book.property_address.city.city.timezone
		# we get available slots from db in order to compare them later
		slots = available_hours_from_db(property_to_book, bookings, b_date=booked_from_dt.date())

		decomposed_booking = decompose_incoming_booking(booked_from_dt, booked_until_dt, timezone)

		intersection = [x for x in slots if x in decomposed_booking]
		if len(intersection) == 0:
			raise serializers.ValidationError(
				"Cannot book with these dates")
		"""
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__lte=attrs["booked_from"]) & Q(booked_until__gte=attrs["booked_from"]), query_1.connector)
		query_1.add(Q(booked_from__lt=attrs["booked_until"]) & Q(booked_until__gte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_from__gte=attrs["booked_from"]) & Q(booked_from__lte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=attrs["booked_until"]) | Q(booked_until=attrs["booked_from"]), query_2.connector)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			raise serializers.ValidationError({
				"dates": "Cannot book with these dates",
			}, code=status.HTTP_409_CONFLICT)
		"""
		return super(HourlyBookingCreateFromOwnerSerializer, self).validate(attrs)

	def create(self, validated_data):

		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		client_email = validated_data.get("client_email")

		property_to_book = self.context['property']
		if property_to_book.booking_type == 100 and property_to_book.price:
			delta = booked_until.date() - booked_from.date()
			price = self.context['property'].price * delta.days
		elif property_to_book.booking_type == 200 and property_to_book.price:
			delta = booked_until - booked_from
			price = self.context['property'].price * delta
		else:
			price = None
		created_booking = Booking(
			number_of_clients=number_of_clients,
			booked_from=booked_from,
			booked_until=booked_until,
			client_email=client_email,
			booked_property_id=self.context["property_id"],
			booked_by=self.context["request"].user,
			price=price
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


class HourlyBookingCreateFromClientSerializer(serializers.ModelSerializer):
	booked_property = PropertyListSerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=True)
	timezone = serializers.SerializerMethodField('get_timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
			'booked_by',
			'created_at',
			'updated_at',
			'id',
			'status'
		]

	def get_timezone(self, obj):
		return self.context['property'].property_address.city.city.timezone

	def validate(self, attrs):
		if attrs["booked_from"] >= attrs["booked_until"]:
			raise serializers.ValidationError({
				'dates': "Dates are not valid"
			})

		property_to_book = self.context['property']

		# dates are retrieved as datetime.datetime
		booked_from_dt = attrs["booked_from"]
		booked_until_dt = attrs["booked_until"]

		# we need to get available days from bd in order to check whether
		# we're booking on an available day
		days = available_days_from_db(property_to_book.availability.open_days)
		# here we check that
		if (booked_from_dt.weekday() not in days) or (booked_until_dt.weekday() not in days):
			raise serializers.ValidationError(
				"Property is not available at that day."
			)

		bookings = Booking.objects.all().filter(
			booked_property=property_to_book,
			booked_from__date=booked_from_dt.date(),
			booked_until__date=booked_until_dt.date()
		)

		timezone = property_to_book.property_address.city.city.timezone
		# we get available slots from db in order to compare them later
		slots = available_hours_from_db(property_to_book, bookings, b_date=booked_from_dt.date())

		decomposed_booking = decompose_incoming_booking(booked_from_dt, booked_until_dt, timezone)

		intersection = [x for x in slots if x in decomposed_booking]
		if len(intersection) == 0:
			raise serializers.ValidationError(
				"Not suitable for available slots.")
		"""
		query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		query_1.add(Q(booked_from__lte=attrs["booked_from"]) & Q(booked_until__gte=attrs["booked_from"]), query_1.connector)
		query_1.add(Q(booked_from__lt=attrs["booked_until"]) & Q(booked_until__gte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_from__gte=attrs["booked_from"]) & Q(booked_from__lte=attrs["booked_until"]), Q.OR)
		query_1.add(Q(booked_property_id=self.context["property_id"]), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from=attrs["booked_until"]) | Q(booked_until=attrs["booked_from"]), query_2.connector)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			raise serializers.ValidationError({
				"dates": "Cannot book with these dates",
			}, code=status.HTTP_409_CONFLICT)
		"""
		return super(HourlyBookingCreateFromClientSerializer, self).validate(attrs)

	def create(self, validated_data):
		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		property_to_book = self.context['property']
		if property_to_book.booking_type == 100 and property_to_book.price:
			delta = booked_until.date() - booked_from.date()
			price = self.context['property'].price * delta.days
		elif property_to_book.booking_type == 200 and property_to_book.price:
			delta = booked_until - booked_from
			price = self.context['property'].price * delta
		else:
			price = None
		created_booking = Booking(
			number_of_clients=number_of_clients,
			booked_from=booked_from,
			booked_until=booked_until,
			client_email=self.context["request"].user.email,
			booked_property_id=self.context["property_id"],
			booked_by=self.context["request"].user,
			price=price
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
	booked_property = PropertyListSerializer(many=False)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'price',
			'timezone',
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
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
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
		queryset = Booking.objects.filter(query_1).exclude(query_2)

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
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
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
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; booking_id: {instance.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return instance


class BookingUpdateClientSerializer(serializers.ModelSerializer):
	number_of_clients = serializers.IntegerField(required=False, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False)

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
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
			queryset = Booking.objects.filter(query_1).exclude(query_2)

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
