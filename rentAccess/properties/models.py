import os
from uuid import uuid4

from django.db import models
import datetime
from register.models import Lock
from django.conf import settings


class PermissionLevels(models.Model):
	p_level = models.PositiveIntegerField(primary_key=True)
	description = models.CharField(max_length=150, null=True, blank=True)


class PropertyPermission(models.Model):
	codename = models.CharField(max_length=100, primary_key=True)
	description = models.CharField(max_length=255, null=True, blank=True)

	def __int__(self):
		return self.codename


class PropertyTypes(models.Model):
	r"""
	Property types are defined by following codes:
		- 100: Ordinary non-inhabitable property, like an office
		- 200: Inhabitable property, a flat or a house
	"""
	property_type = models.IntegerField(primary_key=True, null=False, blank=False)
	description = models.CharField(max_length=150, null=False, blank=False)

	def __int__(self):
		return self.property_type


class Property(models.Model):
	VISIBILITY_CHOICES = [
		(100, 'Publicly Visible'),
		(200, 'Only within the organisation'),
		(300, 'Only owner and admins can see'),
	]
	BOOKING_CHOICES = [
		(200, 'Hourly booking'),
		(100, 'Daily booking'),
	]
	title = models.CharField(max_length=50, null=False, blank=False)
	body = models.TextField(max_length=500, null=False, blank=False)
	price = models.PositiveIntegerField(null=True, blank=True)
	visibility = models.IntegerField(
		choices=VISIBILITY_CHOICES,
		default=100,
		null=False,
		blank=False
	)
	active = models.BooleanField(default=True, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	property_type = models.ForeignKey(
		PropertyTypes,
		to_field='property_type',
		related_name='property_types',
		on_delete=models.CASCADE,
		null=False,
		blank=False
	)
	client_greeting_message = models.CharField(max_length=500, null=False, blank=True)
	requires_additional_confirmation = models.BooleanField(default=False, null=False, blank=True)

	booking_type = models.IntegerField(
		choices=BOOKING_CHOICES,
		default=100,
		null=False,
		blank=False
	)

	def __str__(self):
		return self.title


class Availability(models.Model):
	premises = models.OneToOneField(Property, related_name='availability',
		on_delete=models.CASCADE, null=False, blank=False)
	available_days = models.CharField(max_length=7, default='1111111', null=False, blank=False)

	# interval between bookings in minutes
	booking_interval = models.IntegerField(default=0, null=False, blank=True)

	# maximum number of bookings a day (from 0:00 until 23:59
	# if -1, then no limit
	maximum_number_of_bookings_daily = models.IntegerField(default=-1, null=False, blank=True)

	# maximum length of bookings for the property in minutes
	# if -1, then no limit
	maximum_booking_length = models.IntegerField(default=-1, null=False, blank=True)

	maximum_number_of_clients = models.IntegerField(default=1, null=False, blank=False)

	# these settings are for daily bookings
	departure_time = models.TimeField(null=True, blank=True)
	arrive_until = models.TimeField(null=True, blank=True)
	# these settings are for hourly bookings
	available_from = models.TimeField(null=True, blank=True)
	available_until = models.TimeField(null=True, blank=True)
	available_hours = models.CharField(max_length=255, null=True, blank=True)


class Ownership(models.Model):
	VISIBILITY_CHOICES = [
		(100, 'Publicly Visible'),
		(150, 'Visible for those who booked the property'),
		(200, 'Only within the organisation scope'),
		(250, 'Only within the property owners scope'),
		(300, 'Only property initial owner and admins can see'),
	]

	visibility = models.IntegerField(choices=VISIBILITY_CHOICES, default=250, null=False, blank=True)
	premises = models.ForeignKey(Property, related_name='owners', on_delete=models.CASCADE, null=False, blank=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ownership', on_delete=models.CASCADE, null=False, blank=False)
	is_creator = models.BooleanField(default=False, null=False, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=True)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=True)
	permission_level = models.ForeignKey(PermissionLevels, to_field='p_level',
										related_name='permission_levels',
										on_delete=models.CASCADE)
	#    initial_owner_object = InitialOwnershipManager()

	def __str__(self):
		return str(self.premises.title) + " " + str(self.permission_level_id)


class OwnerPermission(models.Model):
	permission_code = models.ForeignKey(PropertyPermission, to_field='codename',
		on_delete=models.CASCADE, null=False, blank=False)
	owner = models.ForeignKey(Ownership, on_delete=models.CASCADE, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=True)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=True)

	def __str__(self):
		return str(self.owner.user) + " - " + str(self.permission_code.codename)


class PropertyLog(models.Model):
	listed_prop = models.ForeignKey(Property, on_delete=models.CASCADE)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	CHOICES = [
		('POST', 'Post Request'),
		('PUT', 'PUT Request'),
		('PATCH', 'PATCH Request'),
		('DELETE', 'DELETE Request'),
		('DEACTIVATE', 'DEACTIVATE property'),
		('GIVE_ACC', 'Give access to property'),
	]
	action = models.CharField(max_length=300, choices=CHOICES)
	act_time = models.DateTimeField('act_time', null=False, auto_now_add=True)
	result = models.BooleanField('result', null=False)


def path_and_rename(instance, filename):
	path = 'property-images'
	ext = filename.split('.')[-1]
	# get filename
	if instance.pk:
		filename = '{}.{}'.format(instance.pk, ext)
	else:
		# set filename as random string
		filename = '{}.{}'.format(uuid4().hex, ext)
	# return the whole path to the file
	return os.path.join(path, filename)


class PremisesImages(models.Model):
	premises = models.ForeignKey(Property, to_field='id',
								related_name='property_images', on_delete=models.CASCADE)
	image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)
	is_main = models.BooleanField(default=False)

	def set_main(self):
		self.is_main = True


class PremisesAddresses(models.Model):
	premises = models.OneToOneField(Property, related_name='property_address', on_delete=models.CASCADE,
									null=False, blank=False)
	country = models.CharField(max_length=100, blank=False, null=False)
	city = models.CharField(max_length=100, blank=False, null=False)
	street_1 = models.CharField(max_length=100, blank=False, null=False)
	street_2 = models.CharField(max_length=100, blank=True, null=False)
	building = models.CharField(max_length=20, blank=True, null=False)
	floor = models.CharField(max_length=20, blank=True, null=False)
	number = models.CharField(max_length=30, blank=True, null=False)
	zip_code = models.CharField(max_length=10, blank=True, null=False)
	directions_description = models.CharField(max_length=500, blank=True, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)


class LocksWithProperties(models.Model):
	property = models.ForeignKey(Property, to_field='id', on_delete=models.CASCADE,
								related_name="property_with_lock")
	lock = models.ForeignKey(Lock, to_field='uuid', on_delete=models.CASCADE,
							related_name='tied_lock')
	description = models.CharField(max_length=200, blank=True, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
