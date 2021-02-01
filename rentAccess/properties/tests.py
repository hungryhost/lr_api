# if it isn't tested - it isn't done
import datetime
import random
import string
import tempfile
from django.utils.timezone import localtime
import pytz
from unittest import TestCase
from PIL import Image
from .test_utils import (generate_list_of_images, generate_random_string,
										generate_random_list_of_strings,
										generate_random_list_of_numbers)
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from properties.models import PermissionLevels
from bookings.serializers import HourlyBookingsFromOwnerSerializer
from .models import PropertyTypes, Ownership, Property, PremisesAddresses, PremisesImages
from bookings.models import Bookings

User = get_user_model()


class TestsOfProperties(APITestCase):
	r"""
	This class of tests is used for testing of the Properties endpoints.
	What is covered in this test:
		- adding a property
		- changing a property
		- deleting a property
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
		self.owners_list_url = reverse('properties:properties-owners-list', args=[self.correct_response_for_creation_property_JSON["id"]])
		# self.owners_details_url = reverse('properties:owners-details')
		#self.bookings_list_url = reverse('properties:bookings-list')

		self.response_post = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.response_post.data["access"]}')
		self.client_no_auth = APIClient()
		self.client_bad_auth = APIClient()
		self.client_bad_auth.credentials(HTTP_AUTHORIZATION=f'Bearer {self.false_token}')

	def test_create_property(self):

		resp = self.client.post(self.properties_list_url, self.create_property_JSON,
								format='json')
		no_auth_resp = self.client_no_auth.post(self.properties_list_url, self.create_property_JSON,
												format='json')
		bad_auth_resp = self.client_bad_auth.post(self.properties_list_url, self.create_property_JSON,
												  format='json')

		self.assertEqual(no_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(bad_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

		resp.data.pop('created_at')
		resp.data.pop('updated_at')
		ownership_obj = Ownership.objects.get(user=self.correct_response_for_creation_property_JSON["creator_id"],
											  premises=self.correct_response_for_creation_property_JSON["id"])
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(resp.data, self.correct_response_for_creation_property_JSON)

		self.assertEqual(self.registration_json_correct["first_name"], ownership_obj.user.first_name)
		self.assertEqual(self.registration_json_correct["last_name"], ownership_obj.user.last_name)
		self.assertEqual(self.registration_json_correct["email"], ownership_obj.user.email)
		self.assertEqual(400, ownership_obj.permission_level_id)

		self.assertEqual(self.correct_response_for_creation_property_JSON["id"], ownership_obj.premises_id)
		self.assertEqual(self.correct_response_for_creation_property_JSON["title"], ownership_obj.premises.title)
		self.assertEqual(self.correct_response_for_creation_property_JSON["body"], ownership_obj.premises.body)
		self.assertEqual(self.correct_response_for_creation_property_JSON["creator_id"], ownership_obj.user.id)

		created_property = Property.objects.get(pk=resp.data["id"])
		self.assertEqual(created_property.pk, resp.data["id"])
		self.assertEqual(created_property.title, resp.data["title"])
		self.assertEqual(created_property.body, resp.data["body"])
		self.assertEqual(created_property.price, resp.data["price"])
		self.assertEqual(created_property.visibility, 100)
		self.assertEqual(created_property.active, resp.data["active"])
		self.assertEqual(created_property.author.id, resp.data["creator_id"])

		created_address = PremisesAddresses.objects.get(premises=resp.data["id"])
		p_address = resp.data['property_address']
		self.assertEqual(created_address.country, p_address["country"])
		self.assertEqual(created_address.city, p_address["city"])
		self.assertEqual(created_address.building, p_address["building"])
		self.assertEqual(created_address.street_1, p_address["street_1"])
		self.assertEqual(created_address.street_2, p_address["street_2"])
		self.assertEqual(created_address.floor, p_address["floor"])
		self.assertEqual(created_address.number, p_address["number"])
		self.assertEqual(created_address.zip_code, p_address["zip_code"])
		# print(created_property.owners.get(premises=resp.data["id"]).permission_level.p_level)

	def test_update_property(self):
		resp_post = self.client.post(self.properties_list_url, self.create_property_JSON,
									 format='json')
		list_of_titles = generate_random_list_of_strings(10, 30)
		list_of_descriptions = generate_random_list_of_strings(10, 100)
		list_of_prices = generate_random_list_of_numbers()
		# TODO: optimise the loops below so it doesn't look that horrible
		new_property_details_url = reverse('properties:properties-details',
										   args=(resp_post.data["id"],))
		data_for_bad_auth = \
			{
				"title": list_of_titles[random.randint(0, len(list_of_titles) - 1)],
				"body": list_of_descriptions[random.randint(0, len(list_of_descriptions) - 1)],
				"price": 200,
			}
		no_auth_resp = self.client_no_auth.patch(new_property_details_url,
												 data=data_for_bad_auth, format='json')
		bad_auth_resp = self.client_bad_auth.patch(new_property_details_url,
												   data=data_for_bad_auth, format='json')

		# print(bad_auth_resp._headers)
		self.assertEqual(no_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(bad_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

		for i in range(len(list_of_titles)):
			data = {"title": list_of_titles[i]}
			resp_auth = self.client.patch(new_property_details_url,
										  data=data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')
			self.assertEqual(resp_auth.data["title"], list_of_titles[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(list_of_descriptions)):
			data = {"body": list_of_descriptions[i]}
			resp_auth = self.client.patch(new_property_details_url,
										  data=data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')
			self.assertEqual(resp_auth.data["body"], list_of_descriptions[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(list_of_prices)):
			data = {"price": list_of_prices[i]}
			resp_auth = self.client.patch(new_property_details_url,
										  data=data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')
			self.assertEqual(resp_auth.data["price"], list_of_prices[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		# generating sample data for address and updating only one field at a time
		for item in self.address_attr:
			if item not in ['zip_code', 'building', 'floor', 'number']:
				data = {
					item: generate_random_string()
				}
			else:
				if item == 'zip_code':
					data = {
						item: str(random.randint(100000, 999999))
					}
				if item == 'building':
					data = {
						item: str(random.randint(1, 99))
					}
				if item == 'floor':
					data = {
						item: str(random.randint(1, 99))
					}
				if item == 'number':
					data = {
						item: str(random.randint(1, 9999))
					}
			request_data = {
				"property_address": data
			}
			resp_auth = self.client.patch(new_property_details_url,
										  data=request_data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')

			p_address = resp_auth.data['property_address']
			self.assertEqual(data[item], p_address[item])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)
		data_for_update_of_address = \
			{
				"property_address":
					{
						"country": generate_random_string(),
						"city": generate_random_string(),
						"street_1": generate_random_string(),
						"street_2": generate_random_string(),
						"building": str(random.randint(1, 99)),
						"floor": str(random.randint(1, 99)),
						"number": str(random.randint(1, 9999)),
						"zip_code": str(random.randint(100000, 999999))
					}

			}
		data_for_update_of_address["property_address"].pop(self.address_attr[random.randint(1, 2)])
		data_for_update_of_address["property_address"].pop(self.address_attr[random.randint(3, 6)])
		resp_auth = self.client.patch(new_property_details_url,
									  data=data_for_update_of_address, format='json')
		resp_auth.data.pop('created_at')
		resp_auth.data.pop('updated_at')
		self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		created_address = PremisesAddresses.objects.get(premises=resp_auth.data["id"])
		p_address = resp_auth.data['property_address']
		self.assertEqual(created_address.country, p_address["country"])
		self.assertEqual(created_address.city, p_address["city"])
		self.assertEqual(created_address.building, p_address["building"])
		self.assertEqual(created_address.street_1, p_address["street_1"])
		self.assertEqual(created_address.street_2, p_address["street_2"])
		self.assertEqual(created_address.floor, p_address["floor"])
		self.assertEqual(created_address.number, p_address["number"])
		self.assertEqual(created_address.zip_code, p_address["zip_code"])

		created_property = Property.objects.get(pk=resp_auth.data["id"])
		self.assertEqual(created_property.pk, resp_auth.data["id"])
		self.assertEqual(created_property.title, resp_auth.data["title"])
		self.assertEqual(created_property.body, resp_auth.data["body"])
		self.assertEqual(created_property.price, resp_auth.data["price"])
		self.assertEqual(created_property.visibility, 100)
		self.assertEqual(created_property.active, resp_auth.data["active"])
		self.assertEqual(created_property.author.id, resp_auth.data["creator_id"])

	def test_delete_property(self):
		resp_post = self.client.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Property.objects.all().count(), 1)
		self.assertEqual(Property.objects.filter(pk=resp_post.data["id"]).count(), 1)
		resp_post = self.client.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		self.assertEqual(Property.objects.all().count(), 2)
		resp_delete = self.client.delete(
			reverse('properties:properties-details',
			args=(resp_post.data["id"],)),
			format='json')
		self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(Property.objects.all().count(), 1)
		self.assertEqual(Property.objects.filter(pk=resp_post.data["id"]).count(), 0)

	def test_add_images(self):
		resp_post = self.client.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		images = generate_list_of_images()
		resp_auth_1 = self.client.put(
			reverse('properties:properties-images-list',
					args=(resp_post.data["id"],)),
			data={
				'images': [
					images[0],
					images[1],
					images[2],
					images[3],
					images[4],
					images[5],
				],

			},
			format='multipart')
		resp_get = self.client.get(
			reverse('properties:properties-details',
					args=(resp_post.data["id"],)),
			format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		self.assertIsNot(resp_get.data["property_images"], [])
		iterator = 2
		for item in resp_get.data["property_images"]:
			self.assertEqual(len(resp_get.data["property_images"]), PremisesImages.objects.filter(
				premises_id=resp_post.data["id"]).count() - 1)
			self.assertEqual(item["id"], iterator)
			self.assertIsNot(item["image"], "")
			iterator += 1
		obj = PremisesImages.objects.get(premises_id=resp_post.data["id"], is_main=True)
		self.assertEqual(obj.pk, 1)

	def test_change_main_image(self):
		resp_post = self.client.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		resp_auth_1 = self.client.put(
			reverse('properties:properties-main-image-setter',
					args=(resp_post.data["id"],)),
			data={
				"image_id": 1
			},
			format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_404_NOT_FOUND)
		images = generate_list_of_images()
		resp_auth_1 = self.client.put(
			reverse('properties:properties-images-list',
					args=(resp_post.data["id"],)),
			data={
				'images': [
					images[0],
					images[1],
					images[2],
					images[3],
					images[4],
					images[5],
				],
			}, format='multipart')

		resp_auth_1 = self.client.put(
			reverse('properties:properties-main-image-setter',
					args=(resp_post.data["id"],)),
			data={
				"image_id": 3
			},
			format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		resp_get = self.client.get(
			reverse('properties:properties-details',
					args=(resp_post.data["id"],)),
			format='json')

		for item in resp_get.data["property_images"]:
			self.assertEqual(len(resp_get.data["property_images"]),
							 PremisesImages.objects.filter(premises_id=resp_post.data["id"]).count() - 1)
			self.assertIsNot(item["id"], 3)

	def test_delete_images(self):
		resp_post = self.client.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		images = generate_list_of_images()
		resp_auth_1 = self.client.put(
			reverse('properties:properties-images-list',
					args=(resp_post.data["id"],)),
			data={
				'images': [
					images[0],
					images[1],
					images[2],
					images[3],
					images[4],
					images[5],
				],

			},
			format='multipart')
		resp_auth_1 = self.client.delete(reverse('properties:properties-images-list', args=(resp_post.data["id"],)),
										 data={"images": [1, 2, 3]}, format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(PremisesImages.objects.filter(premises_id=resp_post.data["id"], is_main=True).count(), 1)
		self.assertEqual(PremisesImages.objects.filter(premises_id=resp_post.data["id"], is_main=False).count(), 2)

	def test_add_booking_from_owner(self):
		resp_post = self.client.post(self.properties_list_url, self.create_property_JSON,
									format='json')

		resp_create_booking = self.client.post(reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
								data=self.create_booking_JSON, format='json')

		resp_create_booking_wrong_dates = self.client.post(
			reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=self.create_booking_wrong_dates_1_JSON, format='json')
		self.assertEqual(resp_create_booking_wrong_dates.status_code, status.HTTP_400_BAD_REQUEST)

		self.assertEqual(Bookings.objects.all().filter(booked_property=resp_post.data["id"]).count(), 1)

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
		booking_object = Bookings.objects.get(
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
		booking_object = Bookings.objects.get(
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
		booking_object_after_update = Bookings.objects.get(
			booked_property=resp_post.data["id"], id=resp_create_booking.data["id"])

		self.assertEqual(Bookings.objects.get(
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
		booking_object_after_update = Bookings.objects.get(
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
		booking_object_before_update = Bookings.objects.get(
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

	def test_availability_of_property(self):
		resp_post = self.client.post(
			path=self.properties_list_url,
			data=self.create_property_JSON,
			format='json')
		create_booking_json_1 = \
			{
				"number_of_clients": 2,
				"client_email": "test2@test.com",
				"booked_from": "2021-01-01T14:00+0300",
				"booked_until": "2021-01-01T16:00+0300"
			}
		create_booking_json_2 = \
			{
				"number_of_clients": 3,
				"client_email": "test3@test.com",
				"booked_from": "2021-01-01T17:00+0300",
				"booked_until": "2021-01-02T08:00+0300"
			}
		resp_create_booking_1_ok = self.client.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=create_booking_json_1,
			format='json')
		resp_create_booking_2_ok = self.client.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=create_booking_json_2,
			format='json')
		# query = Bookings.objects.all().filter(booked_property_id=1)
		# print(resp_create_booking_1_ok.status_code, resp_create_booking_2_ok.data)

		# datetime_start = "2021-01-01T19:00+0300"
		# datetime_stop = "2021-01-01T20:00+0300"
		# query_1 = Q()
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# query_1.add(Q(booked_from__lte=datetime_start), Q.OR)
		# query_1.add(Q(booked_from__lte=datetime_start) & Q(booked_until__gte=datetime_start), query_1.connector)

		# print(query_1)
		# query_1.add(Q(booked_from__lt=datetime_stop) & Q(booked_until__gte=datetime_stop), Q.OR)
		# query_1.add(Q(booked_from__gte=datetime_start) & Q(booked_from__lte=datetime_stop), Q.OR)
		# query_1.add(Q(booked_property_id=1), Q.AND)
		# print(query_1)
		# if Bookings.objects.filter(
			# query_1
		# ).exists():
			# print("OK")
		# obj = Bookings.objects.get(id=1)
		# print(obj.booked_until.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None))
		availability_list_of_test_cases_ok = [
			{
				"booked_from": "2021-01-01T11:00+0300",  # OK CASE
				"booked_until": "2021-01-01T12:00+0300"
			},
			{
				"booked_from": "2021-01-01T13:00+0300",
				"booked_until": "2021-01-01T14:00+0300"  # OK CASE
			},
			{
				"booked_from": "2021-01-01T16:00+0300",
				"booked_until": "2021-01-01T17:00+0300"  # OK CASE
			},
		]
		availability_list_of_test_cases_not_ok = [
			{
				"booked_from": "2021-01-01T13:00+0300",
				"booked_until": "2021-01-01T15:00+0300"
			},
			{
				"booked_from": "2021-01-01T13:00+0300",
				"booked_until": "2021-01-01T16:00+0300"
			},
			{
				"booked_from": "2021-01-01T14:00+0300",
				"booked_until": "2021-01-01T16:00+0300"
			},
			{
				"booked_from": "2021-01-01T15:00+0300",
				"booked_until": "2021-01-01T16:30+0300"
			},
			{
				"booked_from": "2021-01-01T14:30+0300",
				"booked_until": "2021-01-01T16:30+0300"
			},
		]
		for item in availability_list_of_test_cases_not_ok:
			resp_check_available_not_ok = self.client.post(
				path=reverse('properties:properties-availability-check', args=(resp_post.data["id"],)),
				data=item,
				format='json')
			self.assertEqual(resp_check_available_not_ok.status_code, status.HTTP_409_CONFLICT)
		for item in availability_list_of_test_cases_ok:
			resp_check_available_ok = self.client.post(
				path=reverse('properties:properties-availability-check', args=(resp_post.data["id"],)),
				data=item,
				format='json')
			#print(item, resp_check_available_ok.status_code)
			self.assertEqual(resp_check_available_ok.status_code, status.HTTP_200_OK)

	def test_delete_booking(self):
		pass

	def test_visibility(self):
		pass

	def test_add_owners(self):
		pass

	def test_delete_owners(self):
		pass

	def test_update_owners(self):
		pass

	def test_add_lock(self):
		pass

	def test_delete_lock(self):
		pass
