import json
import pytest
import logging
import datetime
from django.test import TestCase
from django.urls import reverse
from common.models import SupportedCity
from api_tests.pytest_coverage.property_tests.factories import PropertyFactory, PropertyAddressFactory
import properties.models as p_models
import bookings.models as b_models
from api_tests.pytest_coverage.schema_helpers import assert_valid_schema
from api_tests.pytest_coverage.booking_test.e2e_tests.booking_dates_utils import get_booking_date

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


@pytest.mark.e2e_booking_create
class TestCreateDailyBookingSuccess:
	r"""
	These tests cover all possible scenarios of POST requests that
	create properties.

	"""

	@pytest.mark.main
	@pytest.mark.django_db
	@pytest.mark.parametrize("number_of_clients", [
		1, 2, 4, 10, 15, 20])
	@pytest.mark.parametrize("client_email", [
		'client1@lr.ru', 'client2@lr.ru'])
	@pytest.mark.parametrize("booked_from", [
		datetime.date(2021, 3, 29)])
	@pytest.mark.parametrize("booked_until", [
		datetime.date(2021, 3, 30),
		datetime.date(2021, 3, 31),
		datetime.date(2021, 4, 1)

	])
	@pytest.mark.parametrize("_prop", [
		'property_daily_for_booking'])
	def test_post_daily_to_my(
			self,
			db,
			authenticated_clients,
			number_of_clients,
			client_email,
			booked_until,
			booked_from,
			request,
			_prop
	):
		prop, user, client = request.getfixturevalue(
			_prop
		)
		logging.info(f"Response: {prop.booking_type, prop.id}")
		request_json = {
			"number_of_clients": number_of_clients,
			"client_email": client_email,
			"booked_from": get_booking_date(booked_from),
			"booked_until": get_booking_date(booked_until)
		}

		#client1 = authenticated_clients.get()
		response = client.post(
			reverse('properties:properties-bookings-list', args=(prop.id,)),
			request_json,
			format='json'
		)
		logging.info(f"Response: {response.data}")
		logging.info("Validating Database")
		#assert b_models.Booking.objects.count() == 1
		#assert response.status_code == 201

