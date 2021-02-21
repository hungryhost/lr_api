import json
import pytest
import logging

from django.test import TestCase
from django.urls import reverse
from common.models import SupportedCity
from ..factories import PropertyFactory
import properties.models as p_models
from .json_factories import PropertyJsonFactory

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
	@pytest.mark.django_db
	def test_create(self, db, authenticated_clients, property_list_create_endpoint):
		# firstly we get an instance of PropertyFactory
		_property = PropertyFactory.build()
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