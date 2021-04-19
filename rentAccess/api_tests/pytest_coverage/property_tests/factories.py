import datetime
from random import random, randint

import factory
from cities_light.models import Country
from properties import models as p_models
from common import models as com_models
from properties.availability_utils import available_hours_to_db
r"""
Here we define factories for our models that relate to properties
Since we're testing on all levels:
	- models 
	- serializers
	- views
we need factories for all models ready.
"""


def generate_time_from():
	hour = randint(0, 13)
	return datetime.time(hour, 0, 0)


def generate_time_until():
	hour = randint(14, 23)
	return datetime.time(hour, 0, 0)


class PropertyAddressFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = p_models.PremisesAddress

	country = "Russia"
	city = factory.Iterator(com_models.SupportedCity.objects.all())
	street = factory.Faker(
		'street_name'
	)
	building = factory.Faker(
		'building_number'
	)
	floor = factory.Faker(
		'numerify',
		text='%!'
	)
	number = factory.Faker(
		'numerify',
		text='%!!'
	)
	zip_code = factory.Faker(
		'postcode'
	)
	directions_description = factory.Faker(
		'paragraph',
		nb_sentences=2
		)


class PropertyAvailabilityFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = p_models.Availability
	open_days = factory.Faker(
		'bothify',
		text='???????', letters='10'
	)
	available_from = generate_time_from()

	available_until = generate_time_until()

	available_hours = available_hours_to_db(available_from, available_until)

	maximum_number_of_clients = factory.Faker(
		'random_int',
		min=1,
		max=100
	)


class OwnershipFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = p_models.Ownership


class PropertyFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = p_models.Property
	title = factory.Faker('company')
	body = factory.Faker(
		'paragraph',
		nb_sentences=4
		)
	price = factory.Faker(
		'numerify',
		text='%%%!!'
	)
	property_type = factory.Iterator(p_models.PropertyType.objects.all())
	availability = factory.RelatedFactory(
		PropertyAvailabilityFactory,
		factory_related_name='premises'
	)
	property_address = factory.RelatedFactory(
		PropertyAddressFactory,
		factory_related_name='premises'
	)

