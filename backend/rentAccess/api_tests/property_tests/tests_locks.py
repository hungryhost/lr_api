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

User = get_user_model()


class BookingsTests(APITestCase):
	r"""
	Class for testing locks-related endpoints.
	What is covered in this class:


	Note: since this API uses rest_framework_simplejwt we do not test the token
	issuing mechanism, i.e. refresh, verify, etc.
	"""

	def setUp(self) -> None:
		# TODO: add booking-related bodies of resp/req
		PropertyTypes.objects.create(property_type=100, description="Null")
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
		self.create_property_JSON = \
			{
				"title": "test_property_1",
				"body": "test_description_1",
				"price": 100,
				"visibility": 100,
				"property_type": 100,
				"property_address":
					{
						"country": "Country_test_1",
						"city": "City_test_1",
						"street_1": "street_test_1",
						"street_2": "street_test_2",
						"building": "1",
						"floor": "1",
						"number": "1",
						"zip_code": "100000"
					}

			}
		self.correct_response_for_creation_property_JSON = \
			{
				"id": 1,
				"creator_id": 1,
				"title": "test_property_1",
				"body": "test_description_1",
				"property_type": 100,
				"main_image": "",
				"price": 100,
				"active": True,
				"property_address":
					{
						"country": "Country_test_1",
						"city": "City_test_1",
						"street_1": "street_test_1",
						"street_2": "street_test_2",
						"building": "1",
						"floor": "1",
						"number": "1",
						"zip_code": "100000",
						"directions_description": ""
					},
				"client_greeting_message": "",
				"requires_additional_confirmation": False,
				"visibility": 100
			}
		self.create_booking_JSON = \
			{
				"number_of_clients": 1,
				"client_email": "test1@test.com",
				"booked_from": "2020-12-29T17:34+0300",
				"booked_until": "2020-12-29T19:34+0300"
			}
		self.create_booking_wrong_dates_1_JSON = \
			{
				"number_of_clients": 1,
				"client_email": "test1@test.com",
				"booked_from": "2020-12-29T17:34+0300",
				"booked_until": "2020-12-29T16:34+0300"
			}
		self.correct_response_for_creation_booking_JSON = \
			{
				"id": 1,
				"number_of_clients": int(self.create_booking_JSON["number_of_clients"]),
				"client_email": self.create_booking_JSON["client_email"],
				"status": "ACCEPTED",
				"booked_from": "2020-12-29T17:34+0300",
				"booked_until": "2020-12-29T19:34+0300",
				"booked_by": 1
			}
		self.booking_create_response_client_JSON = \
			{

				"booked_property": {
					"id": 1,
					"creator_id": 1,
					"title": "test_property_1",
					"body": "test_description_1",
					"price": 100,
					"active": True,
					"property_type": 100,
					"main_image": "",
					"visibility": 100,
					"property_address": {
						"country": "Country_test_1",
						"city": "City_test_1",
						"street_1": "street_test_1",
						"street_2": "street_test_2",
						"building": "1",
						"floor": "1",
						"number": "1",
						"zip_code": "100000",
						"directions_description": ""
					},
				},
				"number_of_clients": int(self.create_booking_JSON["number_of_clients"]),
				"client_email": self.create_booking_JSON["client_email"],
				"status": "ACCEPTED",
				"booked_from": "2020-12-20T17:34:37.318000+03:00",
				"booked_until": "2020-12-21T17:34:37.318000+03:00",

			}
		# this response is generally shown fro clients
		self.retrieve_booking_response_client_JSON = \
			{
				"id": 1,
				"booked_property": {
					"id": 1,
					"creator_id": 1,
					"title": "test_property_1",
					"body": "test_description_1",
					"price": 100,
					"active": True,
					"property_type": 100,
					"main_image": "",
					"visibility": 100,
					"property_address": {
						"country": "Country_test_1",
						"city": "City_test_1",
						"street_1": "street_test_1",
						"street_2": "street_test_2",
						"building": "1",
						"floor": "1",
						"number": "1",
						"zip_code": "100000",
						"directions_description": ""
					},
					"requires_additional_confirmation": False,
					"client_greeting_message": ""
				},
				"number_of_clients": int(self.create_booking_JSON["number_of_clients"]),
				"client_email": self.create_booking_JSON["client_email"],
				"status": "ACCEPTED",
				"booked_from": "2020-12-29T17:34+0300",
				"booked_until": "2020-12-29T19:34+0300",
				"booked_by": 1,
			}
		self.retrieve_booking_response_admin_JSON = \
			{
				"id": 1,
				"booked_property": {
					"id": 1,
					"creator_id": 1,
					"title": "test_property_1",
					"body": "test_description_1",
					"price": 100,
					"active": True,
					"property_type": 100,
					"main_image": "",
					"visibility": 100,
					"property_address": {
						"country": "Country_test_1",
						"city": "City_test_1",
						"street_1": "street_test_1",
						"street_2": "street_test_2",
						"building": "1",
						"floor": "1",
						"number": "1",
						"zip_code": "100000",
						"directions_description": ""
					},
					"requires_additional_confirmation": False,
					"client_greeting_message": ""
				},
				"number_of_clients": int(self.create_booking_JSON["number_of_clients"]),
				"client_email": self.create_booking_JSON["client_email"],
				"status": "ACCEPTED",
				"booked_from": "2020-12-29T17:34+0300",
				"booked_until": "2020-12-29T19:34+0300",
				"booked_by": 1,
			}
		self.retrieve_booking_response_admin_with_locks_JSON = \
			{
				"id": 1,
				"clients": [
					{
						"existing_id": None,
						"existing_user_url": None,
						"first_name": "test_1_fname",
						"last_name": "test_1_sname",
						"patronymic": "test_1_pname",
						"email": "test1@test.com",
						"description": "some example description"
					}
				],
				"property": [
					{
						# "property_url":""
						"id": 1,
						"creator_id": 1,
						"title": "test_property_1",
						"body": "test_description_1",
						"property_type": 100,
						"price": 100,
						"main_image": "",
						"active": True,
						"property_address": [
							{
								"country": "Country_test_1",
								"city": "City_test_1",
								"street_1": "street_test_1",
								"street_2": "street_test_2",
								"building": "1",
								"floor": "1",
								"number": "1",
								"zip_code": "100000"
							}
						],
						"created_at": "2020-12-08T00:31:45.226645+03:00",
						"updated_at": "2020-12-08T00:31:45.226645+03:00"
					}
				],
				"locks": [
					{
						"id": 1,
						"description": "description"
					}
				],
				"number_of_clients": 1,
				"status": "AWAITING",
				"booked_from": "2020-12-07T14:34:37.318Z",
				"booked_until": "2020-12-07T14:34:37.318Z",
				"booked_by": 1,
				"booked_at": "2020-12-07T14:34:37.318Z",
				"updated_at": "2020-12-07T14:34:37.318Z"
			}
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
		self.owners_list_url = reverse('properties:owners-list',
									   args=[self.correct_response_for_creation_property_JSON["id"]])
		# self.owners_details_url = reverse('properties:owners-details')
		# self.bookings_list_url = reverse('properties:bookings-list')

		self.response_post = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.response_post.data["access"]}')
		self.client_no_auth = APIClient()
		self.client_bad_auth = APIClient()
		self.client_bad_auth.credentials(HTTP_AUTHORIZATION=f'Bearer {self.false_token}')

