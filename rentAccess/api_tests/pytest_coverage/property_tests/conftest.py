import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api_tests.pytest_coverage.user_tests.factories import UserFactory
from .factories import PropertyFactory, OwnershipFactory
from datetime import datetime
import logging
r"""
Here we define common fixtures for all (or most) tests, like api_client that
is used in E2E tests.
"""


@pytest.fixture
def property_list_create_endpoint():
	list_create_endpoint = reverse('properties:properties-list')
	return list_create_endpoint


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
	with django_db_blocker.unblock():
		call_command('loaddata', 'cities_light.json')
		call_command('loaddata', 'property_type.json')
		call_command('loaddata', 'permission_level.json')
		call_command('loaddata', 'common.json')


@pytest.fixture
def authenticated_client():
	client = APIClient()
	user = UserFactory()
	refresh = RefreshToken.for_user(user)
	client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
	return client


@pytest.fixture
def authenticated_clients():
	class ClientFactory(object):
		def get(self):
			client = APIClient()
			user = UserFactory()
			refresh = RefreshToken.for_user(user)
			client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
			return client
	return ClientFactory()


@pytest.fixture(scope='function')
def property_daily(
		db
):
	prop_obj = PropertyFactory(
		booking_type=100,
		price=None
	)
	client = APIClient()
	owner = UserFactory()
	refresh = RefreshToken.for_user(owner)
	client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
	OwnershipFactory(
		premises=prop_obj,
		permission_level_id=400,
		user=owner,
		is_creator=True,
		can_edit=True,
		can_delete=True,
		can_add_images=True,
		can_delete_images=True,
		can_add_bookings=True,
		can_manage_bookings=True,
		can_add_owners=True,
		can_manage_owners=True,
		can_delete_owners=True,
		can_add_locks=True,
		can_manage_locks=True,
		can_delete_locks=True,
		can_add_to_group=True,
		can_add_to_organisation=True,
		is_super_owner=True
	)
	return prop_obj, owner, client


@pytest.fixture(scope='function')
def property_hourly(
		db
):
	prop_obj = PropertyFactory(
		booking_type=200,
		price=None
	)
	client = APIClient()
	owner = UserFactory()
	refresh = RefreshToken.for_user(owner)
	client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
	OwnershipFactory(
		premises=prop_obj,
		permission_level_id=400,
		user=owner,
		is_creator=True,
		can_edit=True,
		can_delete=True,
		can_add_images=True,
		can_delete_images=True,
		can_add_bookings=True,
		can_manage_bookings=True,
		can_add_owners=True,
		can_manage_owners=True,
		can_delete_owners=True,
		can_add_locks=True,
		can_manage_locks=True,
		can_delete_locks=True,
		can_add_to_group=True,
		can_add_to_organisation=True,
		is_super_owner=True
	)
	return prop_obj, owner, client

