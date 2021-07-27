import json
import pytest
import logging

from django.test import TestCase
from django.urls import reverse
from common.models import SupportedCity
from ..factories import PropertyFactory, PropertyAddressFactory
import properties.models as p_models
from .json_factories import PropertyJsonFactory
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

log = logging.getLogger(__name__)


@pytest.mark.e2e_prop_create
class TestCreatePropertySuccess:
	r"""
	These tests cover all possible scenarios of POST requests that
	create properties.

	"""

	@pytest.mark.main
	@pytest.mark.django_db
	@pytest.mark.parametrize("visibility", [
		100, 150, 200, None])
	@pytest.mark.parametrize("active", [
		True, False, None])
	@pytest.mark.parametrize("price", [
		100, None, 6000
	])
	@pytest.mark.parametrize("booking_type", [
		100, 200
	])
	@pytest.mark.parametrize("requires_additional_confirmation", [
		True, False, None
	])
	def test_post(
			self,
			db,
			authenticated_clients,
			property_list_create_endpoint,
			visibility,
			active,
			price,
			requires_additional_confirmation,
			booking_type
	):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(
			booking_type=booking_type,
			visibility=visibility,
			active=active,
			price=price,
			requires_additional_confirmation=requires_additional_confirmation
		)
		# we then make use of it by getting a dict object

		if price is None:
			_json = PropertyJsonFactory(_property).dump_json(
				exclude=['price']
			)
		_json = PropertyJsonFactory(_property).dump_json()
		request_json = _json.copy()
		if requires_additional_confirmation is None:
			request_json.pop('requires_additional_confirmation')
		if _property.active is None:
			request_json.pop('active')
		if _property.visibility is None:
			request_json.pop('visibility')
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			request_json,
			format='json'
		)
		logging.info("Validating Database")
		assert p_models.Property.objects.count() == 1
		assert p_models.Ownership.objects.count() == 1
		assert p_models.Availability.objects.count() == 1
		assert p_models.PremisesAddress.objects.count() == 1
		assert response.status_code == 201
		logging.info(f"Response: {response.data}")
		response.data.pop('id')
		response.data.pop('created_at')
		response.data.pop('updated_at')
		response.data.pop('main_image')
		logging.info("Validating Response Values")
		assert dict(response.data["availability"]) == _json["availability"]
		assert dict(response.data["property_address"]) == _json["property_address"]

		response.data.pop('availability')
		response.data.pop('property_address')
		_json.pop('availability')
		_json.pop('property_address')

		# here we set values to the default ones in order to compare them
		if visibility is None:
			_json['visibility'] = 100
		if active is None:
			_json['active'] = True
		if requires_additional_confirmation is None:
			_json['requires_additional_confirmation'] = False
		assert dict(response.data) == _json

		logging.info("Validating Schema")
		if booking_type == 100:
			assert_valid_schema(json.loads(response.content), '\\properties\\post\\property_post_daily.json')
		else:
			assert_valid_schema(json.loads(response.content), '\\properties\\post\\property_post_hourly.json')


@pytest.mark.e2e_prop_create
@pytest.mark.main
@pytest.mark.django_db
class TestCreatePropertyFail:
	r"""
	Here we create tests for handling responses that are different from
	201 Created, e.g. 400 bad request.
	Usually that happens if a values is not validated.
	"""

	@pytest.mark.parametrize("visibility", [
		101, 151, 202, -102, 'bad'])
	@pytest.mark.parametrize("booking_type", [
		100, 200])
	def test_daily(
			self,
			db,
			authenticated_clients,
			property_list_create_endpoint,
			visibility,
			booking_type
	):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(
			booking_type=booking_type,
			visibility=visibility
		)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		logging.info(
			response.data
		)
		assert p_models.Property.objects.count() == 0
		assert p_models.Ownership.objects.count() == 0
		assert p_models.Availability.objects.count() == 0
		assert p_models.PremisesAddress.objects.count() == 0
		assert response.status_code == 400

	@pytest.mark.parametrize("active", [
		'ok', 5])
	@pytest.mark.parametrize("booking_type", [
		100, 200])
	def test_hourly(
			self,
			db,
			authenticated_clients,
			property_list_create_endpoint,
			active,
			booking_type
	):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(
			booking_type=booking_type,
			active=active,
		)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		logging.info(
			response.data
		)
		assert p_models.Property.objects.count() == 0
		assert p_models.Ownership.objects.count() == 0
		assert p_models.Availability.objects.count() == 0
		assert p_models.PremisesAddress.objects.count() == 0
		assert response.status_code == 400

	@pytest.mark.parametrize("booking_type", [
		300, 'a'])
	def test_booking_type(
			self,
			db,
			authenticated_clients,
			property_list_create_endpoint,
			booking_type
	):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build(
			booking_type=booking_type
		)
		# we then make use of it by getting a dict object
		_json = PropertyJsonFactory(_property).dump_json()
		client1 = authenticated_clients.get()
		response = client1.post(
			property_list_create_endpoint,
			_json,
			format='json'
		)
		logging.info(
			response.data
		)
		assert p_models.Property.objects.count() == 0
		assert p_models.Ownership.objects.count() == 0
		assert p_models.Availability.objects.count() == 0
		assert p_models.PremisesAddress.objects.count() == 0
		assert response.status_code == 400

