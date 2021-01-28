# if it isn't tested - it isn't done
import datetime

import random
import string
import tempfile
from django.utils.timezone import localtime
import pytz
from unittest import TestCase
from PIL import Image
from .json_generator import AddressJson, PropertyJson
from api_tests.user_tests.json_generator import UserRegistrationJSON
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from properties.models import PermissionLevels
from bookings.models import Bookings
from properties.models import PropertyTypes, Ownership, Property, PremisesAddresses, PremisesImages
from ..image_utils import generate_list_of_images
from ..string_utils import (generate_random_string,
                            generate_random_list_of_strings,
                            generate_random_list_of_numbers)

User = get_user_model()


class PropertiesTests(APITestCase, APIClient):
	r"""
	This class of tests is used for testing of the Properties endpoints.
	What is covered in this class:
		- adding a property [OK]
		- changing a property [OK]
		- adding owners
		- changing permissions for owners
		- deleting owners
		- adding images [OK]
		- setting main image [OK]
		- deleting images [NOT OK]
		- retrieving availability [OK]
		- pushing availability
		- deleting a property
		- adding locks
		- changing locks

	"""

	def setUp(self) -> None:
		# TODO: add booking-related bodies of resp/req
		PropertyTypes.objects.create(property_type=100, description="Null")
		PropertyTypes.objects.create(property_type=200, description="Null")
		PermissionLevels.objects.create(p_level=400, description="Null")
		PermissionLevels.objects.create(p_level=300, description="Null")
		PermissionLevels.objects.create(p_level=200, description="Null")
		PermissionLevels.objects.create(p_level=100, description="Null")

		self.false_token = "adamantly"

		self.token_verify_url = reverse('jwtauth:token_verify')
		self.token_obtain_ulr = reverse('jwtauth:token_obtain_pair')
		self.registration_url = "/api/v1/auth/register/"
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
		self.availability_input_daily = \
			{
				"arrival_time_from": "11:00",
				"departure_time_until": "14:00",
				"available_days": [
					0, 1, 3
				],
				"maximum_number_of_clients": 12,
			}
		self.availability_input_hourly = \
			{
				"available_from": "08:00",
				"available_until": "18:00",
				"available_days": [
					0, 1, 3
				],
				"maximum_number_of_clients": 12,
				"booking_interval": 15
			}
		self.create_property_JSON = \
			{
				"title": "test_property_1",
				"body": "test_description_1",
				"price": 100,
				"visibility": 100,
				"property_type": 100,
				"booking_type": 100,
				"availability": self.availability_input_daily,
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

		self.properties_list_url = reverse('properties:properties-list')
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

	def test_create_property(self):
		for user_id in self.responses:
			property_json_1 = PropertyJson(creator_id=user_id)
			property_json_1_request = property_json_1.get_request_json()
			property_request_address_1 = AddressJson().get_address_json()
			property_json_1_request["property_address"] = property_request_address_1
			property_response_json_1 = property_json_1.get_response_json()
			property_response_json_1["property_address"] = property_request_address_1
			property_json_1_request["booking_type"] = 100
			property_json_1_request["availability"] = self.availability_input_daily

			resp = self.list_of_clients[user_id - 1].post(
				path=self.properties_list_url,
				data=property_json_1_request,
				format='json'
			)

			self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
			ownership_obj = Ownership.objects.get(
				user=user_id,
				premises=resp.data["id"])
			created_property = Property.objects.get(pk=resp.data["id"])
			created_address = PremisesAddresses.objects.get(premises=resp.data["id"])
			self.assertEqual(created_property.pk, resp.data["id"])
			resp.data.pop('created_at')
			resp.data.pop('updated_at')

			self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

			self.assertEqual(resp.data["title"], property_response_json_1["title"])
			self.assertEqual(resp.data["body"], property_response_json_1["body"])

			self.assertEqual(resp.data["price"], property_response_json_1["price"])
			self.assertEqual(resp.data["visibility"], property_response_json_1["visibility"])

			self.assertEqual(resp.data["property_address"], property_response_json_1["property_address"])

			self.assertEqual(self.responses[user_id]["personal_info"]["first_name"], ownership_obj.user.first_name)
			self.assertEqual(self.responses[user_id]["personal_info"]["last_name"], ownership_obj.user.last_name)
			self.assertEqual(self.responses[user_id]["personal_info"]["email"], ownership_obj.user.email)
			self.assertEqual(400, ownership_obj.permission_level_id)

			self.assertEqual(resp.data["id"], ownership_obj.premises_id)
			self.assertEqual(property_response_json_1["title"], ownership_obj.premises.title)
			self.assertEqual(property_response_json_1["body"], ownership_obj.premises.body)

			self.assertEqual(created_property.title, resp.data["title"])
			self.assertEqual(created_property.body, resp.data["body"])
			self.assertEqual(created_property.price, resp.data["price"])
			self.assertEqual(created_property.visibility, resp.data["visibility"])
			self.assertEqual(created_property.active, resp.data["active"])

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

		no_auth_resp = self.client_no_auth.post(self.properties_list_url, self.create_property_JSON,
		                                        format='json')
		bad_auth_resp = self.client_bad_auth.post(self.properties_list_url, self.create_property_JSON,
		                                          format='json')
		self.assertEqual(no_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)
		self.assertEqual(bad_auth_resp.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_update_property(self):
		resp_post = self.client_1.post(self.properties_list_url, self.create_property_JSON,
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
			resp_auth = self.client_1.patch(new_property_details_url,
			                                data=data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')
			self.assertEqual(resp_auth.data["title"], list_of_titles[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(list_of_descriptions)):
			data = {"body": list_of_descriptions[i]}
			resp_auth = self.client_1.patch(new_property_details_url,
			                                data=data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')
			self.assertEqual(resp_auth.data["body"], list_of_descriptions[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(list_of_prices)):
			data = {"price": list_of_prices[i]}
			resp_auth = self.client_1.patch(new_property_details_url,
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
			resp_auth = self.client_1.patch(new_property_details_url,
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
		resp_auth = self.client_1.patch(new_property_details_url,
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
		resp_auth = self.client_1.patch(new_property_details_url,
		                                data=self.create_property_JSON, format='json')

	def test_delete_property(self):
		resp_post = self.client_1.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		self.assertEqual(resp_post.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Property.objects.all().count(), 1)
		self.assertEqual(Property.objects.filter(pk=resp_post.data["id"]).count(), 1)
		resp_post = self.client_1.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		self.assertEqual(Property.objects.all().count(), 2)
		resp_delete = self.client_1.delete(
			reverse('properties:properties-details',
			        args=(resp_post.data["id"],)),
			format='json')
		self.assertEqual(resp_delete.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(Property.objects.all().count(), 1)
		self.assertEqual(Property.objects.filter(pk=resp_post.data["id"]).count(), 0)

	def test_add_images(self):
		resp_post = self.client_1.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		images = generate_list_of_images()
		resp_auth_1 = self.client_1.put(
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
		resp_get = self.client_1.get(
			reverse('properties:properties-details',
			        args=(resp_post.data["id"],)),
			format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		self.assertIsNot(resp_get.data["property_images"], [])
		iterator = 1
		for item in resp_get.data["property_images"]:
			self.assertEqual(len(resp_get.data["property_images"]), PremisesImages.objects.filter(
				premises_id=resp_post.data["id"]).count())
			self.assertEqual(item["id"], iterator)
			self.assertIsNot(item["image"], "")
			iterator += 1
		obj = PremisesImages.objects.get(premises_id=resp_post.data["id"], is_main=True)
		self.assertEqual(obj.pk, 1)

	def test_change_main_image(self):
		resp_post = self.client_1.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		resp_auth_1 = self.client_1.put(
			reverse('properties:properties-main-image-setter',
			        args=(resp_post.data["id"],)),
			data={
				"image_id": 1
			},
			format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_404_NOT_FOUND)
		images = generate_list_of_images()
		resp_auth_1 = self.client_1.put(
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

		resp_auth_1 = self.client_1.put(
			reverse('properties:properties-main-image-setter',
			        args=(resp_post.data["id"],)),
			data={
				"image_id": 3
			},
			format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		resp_get = self.client_1.get(
			reverse('properties:properties-details',
			        args=(resp_post.data["id"],)),
			format='json')

		for item in resp_get.data["property_images"]:
			self.assertEqual(len(resp_get.data["property_images"]),
			                 PremisesImages.objects.filter(premises_id=resp_post.data["id"]).count())

	def test_delete_images(self):
		resp_post = self.client_1.post(
			self.properties_list_url,
			self.create_property_JSON,
			format='json')
		images = generate_list_of_images()
		resp_auth_1 = self.client_1.put(
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
		resp_auth_1 = self.client_1.delete(reverse('properties:properties-images-list', args=(resp_post.data["id"],)),
		                                   data={"images": [1, 2, 3]}, format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(PremisesImages.objects.filter(premises_id=resp_post.data["id"], is_main=True).count(), 1)
		self.assertEqual(PremisesImages.objects.filter(premises_id=resp_post.data["id"], is_main=False).count(), 2)

	def test_availability_of_property(self):
		resp_post = self.client_1.post(
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
		resp_create_booking_1_ok = self.client_1.post(
			path=reverse('properties:properties-bookings-list', args=(resp_post.data["id"],)),
			data=create_booking_json_1,
			format='json')
		resp_create_booking_2_ok = self.client_1.post(
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
			resp_check_available_not_ok = self.client_1.post(
				path=reverse('properties:properties-availability-check', args=(resp_post.data["id"],)),
				data=item,
				format='json')
			self.assertEqual(resp_check_available_not_ok.status_code, status.HTTP_409_CONFLICT)
		for item in availability_list_of_test_cases_ok:
			resp_check_available_ok = self.client_1.post(
				path=reverse('properties:properties-availability-check', args=(resp_post.data["id"],)),
				data=item,
				format='json')
			# print(item, resp_check_available_ok.status_code)
			self.assertEqual(resp_check_available_ok.status_code, status.HTTP_200_OK)
