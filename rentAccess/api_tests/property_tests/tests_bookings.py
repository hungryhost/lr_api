import datetime
import random
import string
import tempfile
from django.utils.timezone import localtime
import pytz
from unittest import TestCase
from PIL import Image

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from properties.models import PermissionLevel
from bookings.serializers import HourlyBookingsFromOwnerSerializer
from properties.models import PropertyType, Property
from bookings.models import Booking
User = get_user_model()


class BookingsTests(APITestCase):
	r"""
	Class for testing bookings-related endpoints.

	What is covered in this class:
		- Adding a booking [owners]
		- Adding a booking [clients]
		- Changing a booking [owners]

			- When created by an owner
			- When created by a client
		- Changing a booking [clients]

			- When created by an owner
			- When created by a client
		- Deleting a booking
		- Permissions for adding a booking
		- Permissions for accessing a list of bookings for all properties
		- Permissions for accessing a list of bookings for a single property
		- Permissions for changing a booking
		- Permissions for deleting a booking

	Note: since this API uses rest_framework_simplejwt we do not test the token
	issuing mechanism, i.e. refresh, verify, etc.
	"""

	def setUp(self) -> None:
		# TODO: add booking-related bodies of resp/req
		PropertyType.objects.create(property_type=100, description="Null")
		PermissionLevel.objects.create(p_level=400, description="Null")
		PermissionLevel.objects.create(p_level=300, description="Null")

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
		self.owners_list_url = reverse('properties:properties-owners-list',
									   args=[self.correct_response_for_creation_property_JSON["id"]])
		# self.owners_details_url = reverse('properties:owners-details')
		# self.bookings_list_url = reverse('properties:bookings-list')
		self.client = APIClient()
		self.response_post = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.response_post.data["access"]}')
		self.client_no_auth = APIClient()
		self.client_bad_auth = APIClient()
		self.client_bad_auth.credentials(HTTP_AUTHORIZATION=f'Bearer {self.false_token}')

	def test__booking_from_owner(self):

		resp_create_booking = self.client.post(reverse('properties:properties-bookings-list', args=(1,)),
								data=self.create_booking_JSON, format='json')
		print(resp_create_booking.data)

	def test_add_booking_from_owner(self):
		resp_post = self.client.post(self.properties_list_url, self.create_property_JSON,
									format='json')

		resp_create_booking = self.client.post(reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
								data=self.create_booking_JSON, format='json')

		resp_create_booking_wrong_dates = self.client.post(
			reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=self.create_booking_wrong_dates_1_JSON, format='json')
		self.assertEqual(resp_create_booking_wrong_dates.status_code, status.HTTP_400_BAD_REQUEST)

		self.assertEqual(Booking.objects.all().filter(booked_property=resp_post.data["id"]).count(), 1)

		resp_retrieve_booking = self.client.get(
			reverse('properties:properties-bookings-detail',
					args=(resp_post.data["id"], resp_create_booking.data["id"],)),
			format='json')

		booked_property_from_request = resp_retrieve_booking.data['booked_property']
		booked_property_from_request.pop('created_at')
		booked_property_from_request.pop('updated_at')
		resp_post.data.pop('created_at')
		resp_post.data.pop('updated_at')

		self.assertEqual(dict(booked_property_from_request), self.correct_response_for_creation_property_JSON)
		# since we've checked the correctness of property data, pop it from the response
		resp_retrieve_booking.data.pop('booked_property')
		resp_retrieve_booking.data.pop('created_at')
		resp_retrieve_booking.data.pop('updated_at')
		self.assertEqual(resp_retrieve_booking.data, self.correct_response_for_creation_booking_JSON)
		booking_object = Booking.objects.get(
			booked_property=resp_post.data["id"],
			booked_from=resp_retrieve_booking.data["booked_from"],
			booked_until=resp_retrieve_booking.data["booked_until"])
		serialized_object = HourlyBookingsFromOwnerSerializer(booking_object)

		self.assertEqual(booking_object.status, resp_retrieve_booking.data["status"])
		self.assertEqual(booking_object.client_email, resp_retrieve_booking.data["client_email"])
		self.assertEqual(booking_object.number_of_clients, resp_retrieve_booking.data["number_of_clients"])
		self.assertEqual(serialized_object.data["booked_from"], resp_retrieve_booking.data["booked_from"])
		self.assertEqual(serialized_object.data["booked_until"], resp_retrieve_booking.data["booked_until"])
		self.assertEqual(booking_object.booked_by.id, resp_retrieve_booking.data["booked_by"])
		self.assertEqual(booking_object.id, resp_retrieve_booking.data["id"])

	def test_add_booking_from_client(self):
		resp_post = self.client.post(self.properties_list_url, self.create_property_JSON,
									 format='json')

		client_2 = APIClient()
		client_3 = APIClient()

		response_post_2 = client_2.post(
			path=self.registration_url,
			data=self.registration_json_correct_user_2,
			format='json')

		client_2.credentials(HTTP_AUTHORIZATION=f'Bearer {response_post_2.data["access"]}')
		resp_create_booking = self.client.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=self.create_booking_JSON,
			format='json')
		print(resp_create_booking.data, resp_create_booking.status_code)
		resp_create_booking = self.client.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=self.create_booking_JSON,
			format='json')
		print(resp_create_booking)

	def test_permissions_for_bookings(self):
		resp_post = self.client.post(
			path=self.properties_list_url,
			data=self.create_property_JSON,
			format='json')
		resp_create_booking = self.client.post(
			reverse('properties:properties-bookings-list',
			args=(resp_post.data["id"],)),
			data=self.create_booking_JSON, format='json')
		booking_object = Booking.objects.get(
			booked_property=resp_post.data["id"], id=resp_create_booking.data["id"])
		property_object = Property.objects.get(id=resp_post.data["id"])

		client_2 = APIClient()
		client_3 = APIClient()

		response_post_2 = client_2.post(
			path=self.registration_url,
			data=self.registration_json_correct_user_2,
			format='json')
		response_post_3 = client_3.post(
			path=self.registration_url,
			data=self.registration_json_correct_user_3,
			format='json')

		client_2.credentials(HTTP_AUTHORIZATION=f'Bearer {response_post_2.data["access"]}')
		client_3.credentials(HTTP_AUTHORIZATION=f'Bearer {response_post_3.data["access"]}')

		user_2 = User.objects.get(id=response_post_2.data["personal_info"]["id"])
		user_3 = User.objects.get(id=response_post_3.data["personal_info"]["id"])
		# TODO: refactor to user properties:owners endpoints

		# add owner privileges to the second user
		property_object.owners.create(user=user_2, permission_level_id=300)

		# this response is expected to be with 200 status code
		# since the user is in the list of owners for the booked property
		booking_object_resp_user_2 = client_2.get(
			path=reverse("properties:properties-bookings-detail",
			kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			format='json')

		self.assertEqual(booking_object_resp_user_2.status_code, 200)
		booking_object_resp_user_2.data.pop("created_at")
		booking_object_resp_user_2.data.pop("updated_at")
		booking_object_resp_user_2.data["booked_property"].pop("created_at")
		booking_object_resp_user_2.data["booked_property"].pop("updated_at")
		self.assertEqual(booking_object_resp_user_2.data, self.retrieve_booking_response_admin_JSON)

		# this response is expected to be with 403 status code
		# since the user is not in the list of owners
		booking_object_resp_user_3 = client_3.get(
			path=reverse("properties:properties-bookings-detail",
			kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			format='json')
		self.assertEqual(booking_object_resp_user_3.status_code, status.HTTP_403_FORBIDDEN)
		booking_object_resp_user_3 = client_3.patch(
			path=reverse("properties:properties-bookings-detail",
			kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			data={"status": "DECLINED"},
			format='json')
		self.assertEqual(booking_object_resp_user_3.status_code, status.HTTP_403_FORBIDDEN)
		# ownership_obj = Ownership.objects.filter(premises=self.correct_response_for_creation_property_JSON["id"])
		# print(ownership_obj)

	def test_update_booking_admin_and_creator(self):
		resp_post = self.client.post(
			path=self.properties_list_url,
			data=self.create_property_JSON,
			format='json')
		resp_create_booking = self.client.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=self.create_booking_JSON,
			format='json')

		# add owner privileges to the second user

		booking_object_resp_user_2 = self.client.patch(
			path=reverse("properties:properties-bookings-detail",
			kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			data={"status": "DECLINED"},
			format='json')
		booking_object_after_update = Booking.objects.get(
			booked_property=resp_post.data["id"], id=resp_create_booking.data["id"])

		self.assertEqual(Booking.objects.get(
			booked_property=resp_post.data["id"], id=resp_create_booking.data["id"]).status, "DECLINED")
		self.assertEqual(booking_object_after_update.status, booking_object_resp_user_2.data["status"])

		booking_object_resp_user_2 = self.client.patch(
			path=reverse("properties:properties-bookings-detail",
			kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			data={
				"booked_from": "2020-12-22T17:34:37.318000+03:00",
				"booked_until": "2020-12-23T17:34:37.318000+03:00",
				"status": "ACCEPTED",
				"number_of_clients": 4
			},
			format='json')
		booking_object_after_update = Booking.objects.get(
			booked_property=resp_post.data["id"], id=resp_create_booking.data["id"])
		booking_object_after_update_serialized = HourlyBookingsFromOwnerSerializer(booking_object_after_update)

		self.assertEqual(booking_object_after_update.status, booking_object_resp_user_2.data["status"])
		self.assertEqual(booking_object_after_update.number_of_clients,
						booking_object_resp_user_2.data["number_of_clients"])
		self.assertEqual(booking_object_after_update_serialized.data["booked_from"],
						booking_object_resp_user_2.data["booked_from"])
		self.assertEqual(booking_object_after_update_serialized.data["booked_until"],
						booking_object_resp_user_2.data["booked_until"])

	def test_update_booking_admin_not_creator(self):
		resp_post = self.client.post(
			path=self.properties_list_url,
			data=self.create_property_JSON,
			format='json')
		resp_create_booking = self.client.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=self.create_booking_JSON,
			format='json')
		booking_object_before_update = Booking.objects.get(
			booked_property=resp_post.data["id"], id=resp_create_booking.data["id"])
		serialized_booking_object = HourlyBookingsFromOwnerSerializer(booking_object_before_update)
		client_2 = APIClient()
		client_3 = APIClient()

		response_post_2 = client_2.post(
			path=self.registration_url,
			data=self.registration_json_correct_user_2,
			format='json')

		client_2.credentials(HTTP_AUTHORIZATION=f'Bearer {response_post_2.data["access"]}')
		user_2 = User.objects.get(id=response_post_2.data["personal_info"]["id"])

		# add owner privileges to the second user
		property_object = Property.objects.get(id=resp_post.data["id"])
		property_object.owners.create(user=user_2, permission_level_id=300)

		booking_object_resp_user_2 = client_2.patch(
			path=reverse("properties:properties-bookings-detail",
						kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			data={"status": "DECLINED"},
			format='json')

		self.assertEqual(booking_object_resp_user_2.status_code, status.HTTP_200_OK)
		self.assertEqual(booking_object_resp_user_2.data["status"], "DECLINED")

		booking_object_resp_user_2 = client_2.patch(
			path=reverse("properties:properties-bookings-detail",
						kwargs={"pk": resp_post.data["id"], 'booking_id': resp_create_booking.data["id"]}),
			data={
				"status": "ACCEPTED",
				"booked_until": "2020-12-23T17:34:37.318000+03:00"
			},
			format='json')

		self.assertEqual(booking_object_resp_user_2.status_code, status.HTTP_200_OK)
		self.assertEqual(booking_object_resp_user_2.data["status"], "ACCEPTED")
		self.assertEqual(booking_object_resp_user_2.data["booked_until"],
						serialized_booking_object.data["booked_until"])
		self.assertEqual(booking_object_resp_user_2.data["booked_from"],
						serialized_booking_object.data["booked_from"])