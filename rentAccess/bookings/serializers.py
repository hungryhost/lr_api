from datetime import datetime
from .timezone_utils import utc_to_aware
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers, status
import logging
import pytz
from properties.availability_utils import available_days_from_db, available_hours_from_db, \
	decompose_incoming_booking
from properties.logger_helpers import get_client_ip
from properties.models import Property, Ownership
from properties.serializers import BookedPropertySerializer
from .models import Booking
from .custom_validation_errors import CustomValidation

User = get_user_model()
crud_logger_info = logging.getLogger('rentAccess.properties.crud.info')
owners_logger = logging.getLogger('rentAccess.properties.owners.info')
bookings_logger = logging.getLogger('rentAccess.properties.bookings.info')
images_logger = logging.getLogger('rentAccess.properties.images.info')


class BookedBySerializer(serializers.Serializer):
	first_name = serializers.CharField(max_length=255)
	email = serializers.EmailField()
	class Meta:
		fields = [
			'first_name',
			'email'
		]
		read_only_fields = [
			'first_name',
			'email'
		]


class DailyBookingCreateFromOwnerSerializer(serializers.ModelSerializer):
	booked_property = BookedPropertySerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100, min_value=1)
	booked_from = serializers.DateTimeField(input_formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M"], format="%Y-%m-%d", required=True)
	booked_until = serializers.DateTimeField(input_formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M"], format="%Y-%m-%d", required=True)
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
		tz = pytz.timezone(self.context['property'].property_address.city.city.timezone)
		datetime_ = tz.localize(datetime.now())
		if self.context['property'].availability.maximum_number_of_clients < attrs["number_of_clients"]:
			raise CustomValidation(
				status_code=400,
				field='number_of_clients',
				detail="Number of clients is unacceptable."
			)
			#raise serializers.ValidationError({
			#	'number_of_clients': "Number of clients is unacceptable."
			#})
		if attrs["booked_from"].date() >= attrs["booked_until"].date():
			raise CustomValidation(
				status_code=400,
				field='booked_from',
				detail="Dates are not valid. booked_from >= booked_until"
			)
		if attrs["booked_from"].date() <= datetime_.date():
			raise CustomValidation(
				status_code=400,
				field='booked_from',
				detail="Dates are not valid. booked_from <= date_now"
			)
		if attrs["booked_until"].date() <= datetime_.date():
			raise CustomValidation(
				status_code=400,
				field='booked_until',
				detail="Dates are not valid. booked_until <= date_now"
			)

		if self.context["request"].user.email == attrs["client_email"]:
			raise CustomValidation(
				status_code=400,
				field='client_email',
				detail="Cannot book property you own for yourself."
			)
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
		query_1.add(Q(status__in=['ACCEPTED', 'AWAITING']), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from__date=attrs["booked_until"]) | Q(booked_until__date=attrs["booked_from"]),
		            query_2.connector)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			raise CustomValidation(
				status_code=400,
				field='dates',
				detail="Cannot book with these dates"
			)

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
			datetime.combine(booked_from.date(), property_to_book.availability.available_from),
			timezone
		)
		booked_until_with_tile = utc_to_aware(
			datetime.combine(booked_until.date(), property_to_book.availability.available_until),
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
	booked_property = BookedPropertySerializer(many=False, read_only=True)
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(input_formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M"], format="%Y-%m-%d",
	                                        required=True)
	booked_until = serializers.DateTimeField(input_formats=["%Y-%m-%d", "%Y-%m-%dT%H:%M"], format="%Y-%m-%d",
	                                         required=True)
	timezone = serializers.SerializerMethodField('get_timezone', required=False)
	# price = serializers.FloatField()

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
		tz = pytz.timezone(self.context['property'].property_address.city.city.timezone)
		datetime_ = tz.localize(datetime.now())
		if self.context['property'].availability.maximum_number_of_clients < attrs["number_of_clients"]:
			raise CustomValidation(
				status_code=400,
				field='number_of_clients',
				detail="Number of clients is unacceptable."
			)
		# raise serializers.ValidationError({
		#	'number_of_clients': "Number of clients is unacceptable."
		# })
		if attrs["booked_from"].date() >= attrs["booked_until"].date():
			raise CustomValidation(
				status_code=400,
				field='booked_from',
				detail="Dates are not valid. booked_from >= booked_until"
			)
		if attrs["booked_from"].date() <= datetime_.date():
			raise CustomValidation(
				status_code=400,
				field='booked_from',
				detail="Dates are not valid. booked_from <= date_now"
			)
		if attrs["booked_until"].date() <= datetime_.date():
			raise CustomValidation(
				status_code=400,
				field='booked_until',
				detail="Dates are not valid. booked_until <= date_now"
			)

		if self.context["request"].user.email == attrs["client_email"]:
			raise CustomValidation(
				status_code=400,
				field='client_email',
				detail="Cannot book property you own for yourself."
			)

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
		query_1.add(Q(status__in=['ACCEPTED', 'AWAITING']), Q.AND)
		query_2 = Q()
		query_2.add(Q(booked_from__date=attrs["booked_until"]) | Q(booked_until__date=attrs["booked_from"]),
		            query_2.connector)
		queryset = Booking.objects.filter(query_1).exclude(query_2)
		if queryset.exists():
			raise CustomValidation(
				status_code=400,
				field='dates',
				detail="Cannot book with these dates"
			)

		return super(DailyBookingCreateFromClientSerializer, self).validate(attrs)

	def create(self, validated_data):
		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")

		property_to_book = self.context['property']
		timezone = property_to_book.property_address.city.city.timezone
		booked_from_with_time = utc_to_aware(
			datetime.combine(booked_from.date(), property_to_book.availability.available_from),
			timezone
		)
		booked_until_with_tile = utc_to_aware(
			datetime.combine(booked_until.date(), property_to_book.availability.available_until),
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
	booked_property = BookedPropertySerializer(many=False, read_only=True)
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
			'price',
			'booked_by',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'timezone',
			'booked_property',
			'booked_by',
			'created_at',
			'updated_at',
			'id',
			'status',
			'price'
		]

	def get_timezone(self, obj):
		return self.context['property'].property_address.city.city.timezone

	def validate(self, attrs):
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
		if property_to_book.availability.available_until > property_to_book.availability.available_from:
			if attrs["booked_until"].hour > property_to_book.availability.available_until.hour \
					or attrs["booked_from"].hour < property_to_book.availability.available_from.hour \
					or attrs["booked_from"] >= attrs["booked_until"] \
					or attrs["booked_until"].day - attrs["booked_from"].day > 0 \
					or attrs["booked_until"].month - attrs["booked_from"].month > 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year > 0 \
					or attrs["booked_until"].month - attrs["booked_from"].month < 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year < 0 \
					or attrs["booked_until"].day - attrs["booked_from"].day < 0 \
					or attrs["booked_until"].minute != 0 \
					or attrs["booked_from"].minute != 0:
				raise serializers.ValidationError({
					'dates': "Dates are not valid"
				})
		else:
			if (
					property_to_book.availability.available_until.hour
					< attrs["booked_until"].hour < property_to_book.availability.available_from.hour
			) \
					or (
					property_to_book.availability.available_from.hour >
					attrs["booked_from"].hour > property_to_book.availability.available_until.hour
			) \
					or attrs["booked_from"] >= attrs["booked_until"] \
					or attrs["booked_until"].day - attrs["booked_from"].day > 1 \
					or attrs["booked_until"].month - attrs["booked_from"].month > 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year > 0 \
					or attrs["booked_until"].month - attrs["booked_from"].month < 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year < 0 \
					or attrs["booked_until"].day - attrs["booked_from"].day < 0 \
					or attrs["booked_until"].minute != 0 \
					or attrs["booked_from"].minute != 0:
				raise serializers.ValidationError({
					'dates': "Dates are not valid"
				})
		timezone = property_to_book.property_address.city.city.timezone

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

		return super(HourlyBookingCreateFromOwnerSerializer, self).validate(attrs)

	def create(self, validated_data):

		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		client_email = validated_data.get("client_email")
		price = None
		property_to_book = self.context['property']
		if property_to_book.booking_type == 100 and property_to_book.price:
			delta = booked_until.date() - booked_from.date()
			price = property_to_book.price * int(delta.days)
		if booked_from.hour < booked_until.hour and property_to_book.booking_type == 200 and property_to_book.price :
			delta = booked_until.hour - booked_from.hour
			price = property_to_book.price * int(delta)
		if property_to_book.booking_type == 200 and booked_from.hour > booked_until.hour and property_to_book.price:
			delta = 24 - booked_from.hour + booked_until.hour
			price = property_to_book.price * int(delta)

		created_booking = Booking(
			number_of_clients=number_of_clients,
			booked_from=booked_from,
			booked_until=booked_until,
			client_email=client_email,
			booked_property=self.context['property'],
			booked_by=self.context["request"].user,
			price=price
		)

		if Ownership.objects.filter(
				premises_id=self.context["property_id"],
				user=self.context["request"].user).exists() or (not
		Property.objects.get(id=self.context["property_id"]).requires_additional_confirmation
		):
			created_booking.status = "ACCEPTED"
		created_booking.save()

		return created_booking


class HourlyBookingCreateFromClientSerializer(serializers.ModelSerializer):
	booked_property = BookedPropertySerializer(many=False, read_only=True)
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
			'price',
			'status'
		]

	def get_timezone(self, obj):
		return self.context['property'].property_address.city.city.timezone

	def validate(self, attrs):
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
		if property_to_book.availability.available_until > property_to_book.availability.available_from:
			if attrs["booked_until"].hour > property_to_book.availability.available_until.hour \
					or attrs["booked_from"].hour < property_to_book.availability.available_from.hour \
					or attrs["booked_from"] >= attrs["booked_until"] \
					or attrs["booked_until"].day - attrs["booked_from"].day > 0 \
					or attrs["booked_until"].month - attrs["booked_from"].month > 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year > 0 \
					or attrs["booked_until"].month - attrs["booked_from"].month < 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year < 0 \
					or attrs["booked_until"].day - attrs["booked_from"].day < 0 \
					or attrs["booked_until"].minute != 0 \
					or attrs["booked_from"].minute != 0:
				raise serializers.ValidationError({
					'dates': "Dates are not valid"
				})
		else:
			if (
					property_to_book.availability.available_until.hour
					< attrs["booked_until"].hour < property_to_book.availability.available_from.hour
			) \
					or (
					property_to_book.availability.available_from.hour >
					attrs["booked_from"].hour > property_to_book.availability.available_until.hour
			) \
					or attrs["booked_from"] >= attrs["booked_until"] \
					or attrs["booked_until"].day - attrs["booked_from"].day > 1 \
					or attrs["booked_until"].month - attrs["booked_from"].month > 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year > 0 \
					or attrs["booked_until"].month - attrs["booked_from"].month < 0 \
					or attrs["booked_until"].year - attrs["booked_from"].year < 0 \
					or attrs["booked_until"].day - attrs["booked_from"].day < 0 \
					or attrs["booked_until"].minute != 0 \
					or attrs["booked_from"].minute != 0:
				raise serializers.ValidationError({
					'dates': "Dates are not valid"
				})
		timezone = property_to_book.property_address.city.city.timezone

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

		return super(HourlyBookingCreateFromClientSerializer, self).validate(attrs)

	def create(self, validated_data):
		number_of_clients = validated_data.get("number_of_clients")
		booked_from = validated_data.get("booked_from")
		booked_until = validated_data.get("booked_until")
		property_to_book = self.context['property']
		price = None
		if property_to_book.booking_type == 100 and property_to_book.price:
			delta = booked_until.date() - booked_from.date()
			price = property_to_book.price * int(delta.days)
		if booked_from.hour < booked_until.hour and property_to_book.booking_type == 200 and property_to_book.price:
			delta = booked_until.hour - booked_from.hour
			price = property_to_book.price * int(delta)
		if property_to_book.booking_type == 200 and booked_from.hour > booked_until.hour and property_to_book.price:
			delta = 24 - booked_from.hour + booked_until.hour
			price = property_to_book.price * int(delta)
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
		return created_booking


class BookingsListSerializer(serializers.ModelSerializer):
	booked_property = BookedPropertySerializer(many=False, read_only=True)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False,
	                                 read_only=True)
	available_actions = serializers.SerializerMethodField('get_available_actions')
	booked_by_info = serializers.SerializerMethodField('get_booked_by_info')

	class Meta:
		model = Booking
		fields = (
			'id',
			'available_actions',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'cancelled_reason',
			'price',
			'timezone',
			'booked_from',
			'booked_until',
			'booked_by',
			'booked_by_info',
			'created_at',
			'updated_at'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'cancelled_reason',
			'price',
			'timezone',
			'booked_from',
			'booked_until',
			'booked_by',
			'created_at',
			'updated_at',
			'booked_by_info'
		]

	def to_representation(self, instance):
		representation = super().to_representation(instance)
		timezone = instance.booked_property.property_address.city.city.timezone
		localtz = pytz.timezone(timezone)
		dt_aware = instance.booked_until.replace(tzinfo=localtz)
		if dt_aware < datetime.now(tz=localtz):
			representation['status'] = 'EXPIRED'
		return representation

	def get_booked_by_info(self, instance):
		serializer = BookedBySerializer(instance.booked_by)
		return serializer.data

	def get_available_actions(self, instance):
		owners = instance.booked_property.owners.all()
		currently_owner = None
		status_can_be_updated = False
		number_of_clients_can_be_updated = False
		can_be_cancelled_by_user = False
		for owner in owners:
			if self.context['request'].user == owner.user:
				currently_owner = owner
		if currently_owner:
			if currently_owner.can_manage_bookings:
				status_can_be_updated = True
				can_be_cancelled_by_user = True
			if instance.booked_by == currently_owner.user:
				number_of_clients_can_be_updated = True
				can_be_cancelled_by_user = True
		if self.context['request'].user.email == instance.client_email:
			number_of_clients_can_be_updated = True
			can_be_cancelled_by_user = True

		if instance.status == 'ACCEPTED':
			status_can_be_updated = False

		timezone = instance.booked_property.property_address.city.city.timezone
		localtz = pytz.timezone(timezone)
		dt_aware = instance.booked_until.replace(tzinfo=localtz)
		if dt_aware < datetime.now(tz=localtz) or \
				instance.status in ['CANCELLED_BY_CLIENT', 'CANCELLED_BY_OWNER', 'EXPIRED']:
			status_can_be_updated = False
			number_of_clients_can_be_updated = False
			can_be_cancelled_by_user = False
		return_dict = {
			"status_can_be_updated": status_can_be_updated,
			"number_of_clients_can_be_updated": number_of_clients_can_be_updated,
			"can_be_cancelled_by_user": can_be_cancelled_by_user
		}
		return return_dict


class BookingUpdateAdminAndCreatorSerializer(serializers.ModelSerializer):
	booked_property = BookedPropertySerializer(many=False, read_only=True)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False, read_only=True)
	_meta_ = serializers.SerializerMethodField('get_meta_info')

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'cancelled_reason',
			'booked_from',
			'booked_until',
			'timezone',
			'price',
			'booked_by',
			'created_at',
			'updated_at',
			'_meta_'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'client_email',
			'booked_from',
			'booked_until',
			'cancelled_reason',
			'timezone',
			'price',
			'booked_by',
			'created_at',
			'updated_at',
			'_meta_'
		]

	def get_meta_info(self, obj):
		return {
			"S_ID": "B-U-AAC-1",
			"ACT": "PUT",
			"API": "LR_S_API_100",
			"TIMESTAMP": datetime.now()
		}

	def update(self, instance, validated_data):
		status = validated_data.get("status", None)
		number_of_clients = validated_data.get("number_of_clients", None)
		if status:
			instance.status = status
		if number_of_clients:
			instance.number_of_clients = number_of_clients
		instance.save()
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; booking_id: {instance.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return instance


class BookingUpdateAdminNotCreatorSerializer(serializers.ModelSerializer):
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone',
	                                 required=False, read_only=True)
	booked_property = BookedPropertySerializer(many=False, read_only=True)
	_meta_ = serializers.SerializerMethodField('get_meta_info')

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'cancelled_reason',
			'booked_from',
			'booked_until',
			'timezone',
			'price',
			'booked_by',
			'created_at',
			'updated_at',
			'_meta_'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'booked_from',
			'booked_until',
			'timezone',
			'price',
			'cancelled_reason',
			'booked_by',
			'created_at',
			'updated_at',
			'_meta_'
		]

	def get_meta_info(self, obj):
		return {
			"S_ID": "B-U-ANC-1",
			"ACT": "PUT",
			"API": "LR_S_API_100",
			"TIMESTAMP": datetime.now()
		}

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
	number_of_clients = serializers.IntegerField(required=True, max_value=100)
	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False, read_only=True)
	booked_property = BookedPropertySerializer(many=False, read_only=True)
	_meta_ = serializers.SerializerMethodField('get_meta_info')

	class Meta:
		model = Booking
		fields = (
			'id',
			'booked_property',
			'number_of_clients',
			'client_email',
			'status',
			'cancelled_reason',
			'booked_from',
			'booked_until',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at',
			'_meta_'
		)
		read_only_fields = [
			'id',
			'booked_property',
			'client_email',
			'status',
			'booked_from',
			'booked_until',
			'cancelled_reason',
			'timezone',
			'booked_by',
			'created_at',
			'updated_at',
			'_meta_'
		]

	def get_meta_info(self, obj):
		return {
			"S_ID": "B-U-CL-1",
			"ACT": "PUT",
			"API": "LR_S_API_100",
			"TIMESTAMP": datetime.now()
		}

	def update(self, instance, validated_data):
		number_of_clients = validated_data.get("number_of_clients", None)
		if number_of_clients:
			instance.number_of_clients = number_of_clients
		instance.save()
		bookings_logger.info(
			f"object: booking; stage: serialization; action_type: create; "
			f"user_id: {self.context['request'].user.id}; property_id: {self.context['property_id']}; booking_id: {instance.id} "
			f"ip_addr: {get_client_ip(self.context['request'])}; status: OK;")

		return instance


class CancelBookingSerializer(serializers.ModelSerializer):
	cancelled_reason = serializers.CharField(max_length=255, required=True, allow_blank=False)

	booked_from = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	booked_until = serializers.DateTimeField(format="%Y-%m-%dT%H:%M%z", required=False, read_only=True)
	timezone = serializers.CharField(source='booked_property.property_address.city.city.timezone', required=False,
	                                 read_only=True)
	booked_property = BookedPropertySerializer(many=False, read_only=True)

	class Meta:
		model = Booking
		fields = [
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
			'cancelled_reason',
			'updated_at'
		]
		read_only_fields = [
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
			'updated_at',
		]

	def get_meta_info(self, obj):
		return {
			"S_ID"     : "B-U-CL-1",
			"ACT"      : "PUT",
			"API"      : "LR_S_API_100",
			"TIMESTAMP": datetime.now()
		}

	def update(self, instance, validated_data):
		if instance.status in ['CANCELLED_BY_CLIENT', 'CANCELLED_BY_OWNER']:
			raise serializers.ValidationError({
				"status": "the booking is already cancelled."
			})
		cancelled_reason = validated_data.get("cancelled_reason", None)
		if self.context['request'].user.email == instance.client_email:
			instance.status = 'CANCELLED_BY_CLIENT'
		else:
			instance.status = 'CANCELLED_BY_OWNER'
		if cancelled_reason:
			instance.cancelled_reason = cancelled_reason
		instance.save()
		return instance
