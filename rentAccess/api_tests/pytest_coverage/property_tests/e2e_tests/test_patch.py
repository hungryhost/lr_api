import json
import pytest
import logging

from django.test import TestCase
from django.urls import reverse
from common.models import SupportedCity
from ..factories import PropertyFactory, PropertyAddressFactory, PropertyAvailabilityFactory
import properties.models as p_models
from .json_factories import PropertyJsonFactory, AvailabilityJsonFactory
from api_tests.pytest_coverage.schema_helpers import assert_valid_schema

r"""
Since tests are being refactored we now focus on making a class
for each actions with endpoints. 

These tests strongly rely on two external files:
		- ../factories.py: this file makes use of factory_boy and
		creates factories for models in order to run tests
		- ./json_factories.py: this file in turn makes use of our factories
		and returns dict objects that we pass in the requests and use extensively
		as well.
		
	Changes in those files should not affect the structure of the tests, making
	them independent of the models or structures of the requests that may
	change.
	
We also make use of various conftest.py files on different levels from which we take endpoints and
instances of (authenticated) ApiClient class and many more.
"""


@pytest.mark.main
@pytest.mark.django_db
class TestUpdatePropertySuccess:
	r"""
	These tests are aimed to test only PATCH requests for existing properties.
	In order to perform these tests following conditions must be met:
		- A valid JSON schema in directory \\properties\\patch
		- A fixture for an authenticated user
		- Fixtures for 2 properties: with daily and hourly booking types

	We do not test permissions here: such tests performed separately and we
	assume that the authenticated user has appropriate permissions for PATCH requests.
	"""

	@pytest.mark.parametrize(
		'field',
		[
			"country",
			"city",
			"street",
			"building",
			"floor",
			"number",
			"zip_code",
			"directions_description"
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_address(
			self,
			db,
			field,
			_property,
			request,
	):
		prop, user, client = request.getfixturevalue(
			_property
		)
		address = PropertyAddressFactory.build()
		address_dict = {
			"property_address": {
				"country"               : address.country,
				"city"                  : address.city.name,
				"street"                : address.street,
				"building"              : address.building,
				"floor"                 : address.floor,
				"number"                : address.number,
				"zip_code"              : address.zip_code,
				"directions_description": address.directions_description
			}
		}
		valid_field = address_dict['property_address'][field]
		address_to_change = {
			"property_address":
				{
					field: valid_field
				}
		}
		logging.info(
			address_to_change
		)
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=address_to_change,
			format='json'
		)
		logging.info(
			response.data
		)
		assert response.status_code == 200
		assert response.data["property_address"][field] == valid_field

	@pytest.mark.parametrize(
		'field',
		[
			"title",
			"body",
			"price",
			"client_greeting_message"
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_main_info(
			self,
			db,
			field,
			_property,
			request,
	):
		prop, user, client = request.getfixturevalue(
			_property
		)
		_newProperty = PropertyFactory.build()
		fields_dict = {
			"title"                           : _newProperty.title,
			"body"                            : _newProperty.body,
			"price"                           : _newProperty.price,
			"client_greeting_message"         : _newProperty.client_greeting_message
		}
		valid_field = fields_dict[field]
		field_to_change = {
				field: valid_field
		}
		logging.info(
			field_to_change
		)
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=field_to_change,
			format='json'
		)
		logging.info(
			response.data
		)
		assert response.status_code == 200
		field_type = type(response.data[field])
		assert response.data[field] == field_type(valid_field)

	@pytest.mark.parametrize(
		'visibility',
		[
			100,
			150,
			200
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_visibility(
			self,
			db,
			_property,
			request,
			visibility
	):
		prop, user, client = request.getfixturevalue(
			_property
		)

		field_to_change = {
			"visibility": visibility
		}

		logging.info(
			field_to_change
		)
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=field_to_change,
			format='json'
		)
		logging.info(
			response.data
		)
		assert response.status_code == 200
		assert response.data['visibility'] == field_to_change['visibility']

	@pytest.mark.parametrize(
		'price',
		[
			0,
			1000,
			5000,
			None
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_price(
			self,
			db,
			_property,
			request,
			price
	):
		prop, user, client = request.getfixturevalue(
			_property
		)

		field_to_change = {
			"price": price
		}

		logging.info(
			field_to_change
		)
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=field_to_change,
			format='json'
		)
		logging.info(
			response.data
		)
		assert response.status_code == 200
		assert response.data['price'] == field_to_change['price']

	@pytest.mark.parametrize(
		'property_type',
		[
			100,
			200
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_property_type(
			self,
			db,
			_property,
			request,
			property_type
	):
		prop, user, client = request.getfixturevalue(
			_property
		)

		field_to_change = {
			"property_type": property_type
		}
		logging.info(
			field_to_change
		)
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=field_to_change,
			format='json'
		)
		logging.info(
			response.data
		)
		assert response.status_code == 200
		assert response.data['property_type'] == field_to_change['property_type']

	@pytest.mark.parametrize(
		'requires_additional_confirmation',
		[
			True,
			False
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_requires_additional_confirmation(
			self,
			db,
			_property,
			request,
			requires_additional_confirmation
	):
		prop, user, client = request.getfixturevalue(
			_property
		)

		field_to_change = {
			"requires_additional_confirmation": requires_additional_confirmation
		}

		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=field_to_change,
			format='json'
		)
		logging.info(f"Request: {field_to_change}")
		logging.info(f"Response: {response.data}")
		assert response.status_code == 200
		assert response.data['requires_additional_confirmation'] \
		       == field_to_change['requires_additional_confirmation']

	@pytest.mark.parametrize(
		'active',
		[
			True,
			False
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_active(
			self,
			db,
			_property,
			request,
			active
	):
		prop, user, client = request.getfixturevalue(
			_property
		)

		field_to_change = {
			"active": active
		}
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=field_to_change,
			format='json'
		)
		logging.info(f"Request: {field_to_change}")
		logging.info(f"Response: {response.data}")
		assert response.status_code == 200
		assert response.data['active'] == field_to_change['active']

	@pytest.mark.parametrize(
		'field',
		[
			"arrival_time_from",
			"departure_time_until",
			"open_days",
			"maximum_number_of_clients",
		])
	def test_update_availability_daily(
			self,
			db,
			field,
			property_daily,
	):
		prop, user, client = property_daily
		new_availability = PropertyAvailabilityFactory.build()
		availability_dict = AvailabilityJsonFactory(
			availability=new_availability, booking_type=100).dump_json()
		request_json = {
			"availability": {
				field: availability_dict[field]
			}
		}
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=request_json,
			format='json'
		)
		initial_availability = AvailabilityJsonFactory(
			availability=prop.availability, booking_type=100).dump_json()
		logging.info(f"Initial Availability: {initial_availability}")
		logging.info(f"Request: {request_json}")
		logging.info(f"Response: {response.data}")
		assert response.status_code == 200
		assert response.data['availability'][field] == availability_dict[field]

	@pytest.mark.parametrize(
		'field',
		[
			"available_from",
			"available_until",
			"open_days",
			"maximum_number_of_clients",
		])
	def test_update_availability_hourly(
			self,
			db,
			field,
			property_hourly,
	):
		prop, user, client = property_hourly
		new_availability = PropertyAvailabilityFactory.build()
		availability_dict = AvailabilityJsonFactory(
			availability=new_availability, booking_type=200).dump_json()
		request_json = {
			"availability": {
				field: availability_dict[field]
			}
		}
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=request_json,
			format='json'
		)
		initial_availability = AvailabilityJsonFactory(
			availability=prop.availability, booking_type=200).dump_json()
		logging.info(f"Initial Availability: {initial_availability}")
		logging.info(f"Request: {request_json}")
		logging.info(f"Response: {response.data}")
		assert response.status_code == 200
		assert response.data['availability'][field] == availability_dict[field]

	@pytest.mark.parametrize(
		'booking_type',
		[
			100, 200
		])
	def test_update_booking_type(
			self,
			db,
			booking_type,
			request
	):
		if booking_type == 100:
			prop, user, client = request.getfixturevalue(
				'property_daily'
			)
			new_availability = PropertyAvailabilityFactory.build()
			availability_dict = AvailabilityJsonFactory(
				availability=new_availability, booking_type=100).dump_json()
			initial_availability = AvailabilityJsonFactory(
				availability=prop.availability, booking_type=200).dump_json()
		else:
			prop, user, client = request.getfixturevalue(
				'property_hourly'
			)
			new_availability = PropertyAvailabilityFactory.build()
			availability_dict = AvailabilityJsonFactory(
				availability=new_availability, booking_type=200).dump_json()
			initial_availability = AvailabilityJsonFactory(
				availability=prop.availability, booking_type=100).dump_json()
		request_json = {"booking_type": booking_type, "availability": availability_dict}
		response = client.patch(
			path=reverse('properties:properties-details', args=(prop.id,)),
			data=request_json,
			format='json'
		)

		logging.info(f"Initial Availability: {initial_availability}")
		logging.info(f"Request: {request_json}")
		logging.info(f"Response: {response.data}")
		assert response.status_code == 200
		assert response.data['availability'] == availability_dict
		assert response.data['booking_type'] == request_json['booking_type']

	@pytest.mark.parametrize(
		'field',
		[
			"title",
			"body",
			"price",
			"visibility",
			"active",
			"property_type",
			"client_greeting_message",
			"requires_additional_confirmation"
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_full_same_booking_type(
			self,
			db,
			field,
			_property,
			request,
	):
		pass

	@pytest.mark.parametrize(
		'field',
		[
			"title",
			"body",
			"price",
			"visibility",
			"active",
			"property_type",
			"client_greeting_message",
			"requires_additional_confirmation"
		])
	@pytest.mark.parametrize(
		'_property',
		[
			'property_daily',
			'property_hourly'
		]
	)
	def test_update_full_changed_booking_type(
			self,
			db,
			field,
			_property,
			request,
	):
		pass