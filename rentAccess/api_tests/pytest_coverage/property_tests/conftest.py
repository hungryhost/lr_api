import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from api_tests.pytest_coverage.user_tests.factories import UserFactory

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
