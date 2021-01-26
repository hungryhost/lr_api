# if it isn't tested - it isn't done
import datetime
import random
import string
import tempfile
from django.utils.timezone import localtime
import pytz
from unittest import TestCase
from PIL import Image
from properties.test_utils import (generate_list_of_images, generate_random_string,
										generate_random_list_of_strings,
										generate_random_list_of_numbers)
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from common.models import PermissionLevels
from properties.serializers import BookingsSerializer

from properties.models import PropertyTypes, Ownership, Property, PremisesAddresses, PremisesImages, Bookings
from api_tests.user_tests.json_generator import UserRegistrationJSON

User = get_user_model()


class BookingsTests(APITestCase):
	r"""
	Class for testing locks-related endpoints.
	What is covered in this class:
		- Adding a lock for the property
		- Changing a lock
		- Deleting a lock
		- Retrieving a lock
		- Adding multiple locks for the property
		- Adding card for the lock on the property
		- Adding a master-key for the lock on the property
		- Permissions for adding locks
		- Permissions for adding cards
		- Permissions for adding master-keys
		- Permissions for accessing a list of locks
		- Permissions for accessing info about a single lock
		- Permissions for changing a lock
		- Permissions for deleting a lock

	Note: since this API uses rest_framework_simplejwt we do not test the token
	issuing mechanism, i.e. refresh, verify, etc.
	"""

	def setUp(self) -> None:
		# TODO: add booking-related bodies of resp/req
		PropertyTypes.objects.create(property_type=100, description="Null")
		PropertyTypes.objects.create(property_type=200, description="Null")
		PermissionLevels.objects.create(p_level=400, description="Null")
		PermissionLevels.objects.create(p_level=300, description="Null")

		self.false_token = "adamantly"

		self.token_verify_url = reverse('jwtauth:token_verify')
		self.token_obtain_ulr = reverse('jwtauth:token_obtain_pair')
		self.registration_url = reverse('jwtauth:register')
		self.login_url = reverse('jwtauth:token_obtain_pair')
		self.logout_url = reverse('jwtauth:logout')
		self.logout_all_url = reverse('jwtauth:logout_all')
		self.address_attr = [
			'country',
			'city',
			'street_1',
			'street_2',
			'building',
			'floor',
			'number',
			'zip_code'
		]
		self.register_access_response_JSON = \
			{
				"id": 1,
				"code": 1234,
				"access_start": "2020-12-07T14:34:37.318Z",
				"access_stop": "2020-12-07T14:34:37.318Z",
			}
		self.registration_json_correct = \
			{
				"first_name": "test_case_fn",
				"last_name": "test_case_ln",
				"email": "test_case_email@test.com",
				"password": "test_pass_test_pass",
				"password2": "test_pass_test_pass"
			}
		self.registration_json_correct_user_2 = \
			{
				"first_name": "test_case_fn2",
				"last_name": "test_case_ln2",
				"email": "test_case_email2@test.com",
				"password": "test_pass_test_pass2",
				"password2": "test_pass_test_pass2"
			}
		self.registration_json_correct_user_3 = \
			{
				"first_name": "test_case_fn3",
				"last_name": "test_case_ln3",
				"email": "test_case_email3@test.com",
				"password": "test_pass_test_pass3",
				"password2": "test_pass_test_pass3"
			}
		self.properties_list_url = reverse('properties:properties-list')
		#self.owners_list_url = reverse('properties:properties-owners-list', args=[self.correct_response_for_creation_property_JSON["id"]])
		# self.owners_details_url = reverse('properties:owners-details')
		#self.bookings_list_url = reverse('properties:bookings-list')
		self.client_1 = APIClient()
		self.client_2 = APIClient()
		self.client_3 = APIClient()
		self.client_4 = APIClient()
		self.client_5 = APIClient()
		self.client_6 = APIClient()
		self.client_7 = APIClient()
		self.client_8 = APIClient()
		self.client_9 = APIClient()
		self.client_10 = APIClient()

		self.list_of_clients = [
			self.client_1, self.client_2, self.client_3, self.client_4,
			self.client_5, self.client_6, self.client_7, self.client_8,
			self.client_9, self.client_10
		]
		self.responses = {}
		self.client_id = 1

		for client in self.list_of_clients:
			client_json = UserRegistrationJSON().get_request_json()
			response_post = client.post(
				path=self.registration_url,
				data=client_json,
				format='json')
			self.responses[self.client_id] = response_post.data
			self.client_id += 1
			client.credentials(HTTP_AUTHORIZATION=f'Bearer {response_post.data["access"]}')
		self.client_no_auth = APIClient()
		self.client_bad_auth = APIClient()
		self.client_bad_auth.credentials(HTTP_AUTHORIZATION=f'Bearer {self.false_token}')

