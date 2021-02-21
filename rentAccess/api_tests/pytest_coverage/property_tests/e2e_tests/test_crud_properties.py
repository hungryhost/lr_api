import json
import pytest
import logging

from django.test import TestCase
from django.urls import reverse
from common.models import SupportedCity
from ..factories import PropertyFactory
import properties.models as p_models
from .json_factories import PropertyJsonFactory
from .schema_helpers import assert_valid_schema

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


class TestCreateProperty:
	r"""
	These tests cover all possible scenarios of POST requests that
	create properties.

	"""
	@pytest.mark.main
	@pytest.mark.django_db
	def test_daily(self, db, authenticated_clients, property_list_create_endpoint):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(booking_type=100)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		assert p_models.Property.objects.count() == 1
		assert p_models.Ownership.objects.count() == 1
		assert p_models.Availability.objects.count() == 1
		assert p_models.PremisesAddress.objects.count() == 1
		assert response.status_code == 201
		assert_valid_schema(json.loads(response.content), '\\properties\\post\\property_post_daily.json')

	@pytest.mark.main
	@pytest.mark.django_db
	def test_hourly(self, db, authenticated_clients, property_list_create_endpoint):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(booking_type=200)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		assert p_models.Property.objects.count() == 1
		assert p_models.Ownership.objects.count() == 1
		assert p_models.Availability.objects.count() == 1
		assert p_models.PremisesAddress.objects.count() == 1
		assert response.status_code == 201
		assert_valid_schema(json.loads(response.content), '\\properties\\post\\property_post_hourly.json')

	@pytest.mark.main
	@pytest.mark.django_db
	@pytest.mark.parametrize("price", [
		100, 200, 1000, 2000, 5000, 10000,
		pytest.param(-1000, marks=pytest.mark.xfail)])
	def test_daily_with_price(self, db, price, authenticated_clients, property_list_create_endpoint):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(booking_type=100, price=price)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		assert p_models.Property.objects.count() == 1
		assert p_models.Ownership.objects.count() == 1
		assert p_models.Availability.objects.count() == 1
		assert p_models.PremisesAddress.objects.count() == 1
		assert response.status_code == 201
		assert_valid_schema(json.loads(response.content), '\\properties\\post\\property_post_daily.json')

	@pytest.mark.main
	@pytest.mark.django_db
	@pytest.mark.parametrize("price", [
		100, 200, 1000, 2000, 5000, 10000,
		pytest.param(-1000, marks=pytest.mark.xfail)])
	def test_hourly_with_price(self, db, price, authenticated_clients, property_list_create_endpoint):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(booking_type=200, price=price)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		assert p_models.Property.objects.count() == 1
		assert p_models.Ownership.objects.count() == 1
		assert p_models.Availability.objects.count() == 1
		assert p_models.PremisesAddress.objects.count() == 1
		assert response.status_code == 201
		assert_valid_schema(json.loads(response.content), '\\properties\\post\\property_post_hourly.json')


class TestUpdateProperty:
	r"""
	These tests are aimed to test only PATCH requests for existing properties.
	In order to perform these tests following conditions must be met:
		- A valid JSON schema in directory \\properties\\patch
		- A fixture for an authenticated user
		- Fixtures for 2 properties: with daily and hourly booking types

	We do not test permissions here: such tests performed separately and we
	assume that the authenticated user has appropriate permissions for PATCH requests.
	"""
	@pytest.mark.main
	@pytest.mark.django_db
	def test_update_daily_main_info(
			self,
			db,
			authenticated_clients,
			property_list_create_endpoint
	):
		pass