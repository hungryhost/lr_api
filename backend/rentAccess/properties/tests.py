import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from common.models import PermissionLevels
from .models import PropertyTypes, Ownership, Property, PremisesAddresses

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
		PropertyTypes.objects.create(property_type=100, description="Null")
		PermissionLevels.objects.create(p_level=400, description="Null")

		self.false_token = "adamantly"

		self.token_verify_url = reverse('jwtauth:token_verify')
		self.token_obtain_ulr = reverse('jwtauth:token_obtain_pair')
		self.registration_url = reverse('jwtauth:register')
		self.login_url = reverse('jwtauth:token_obtain_pair')
		self.logout_url = reverse('jwtauth:logout')
		self.logout_all_url = reverse('jwtauth:logout_all')

		self.properties_list_url = reverse('properties:property-list')
		self.properties_details_url = reverse('properties:properties-details')
		self.owners_list_url = reverse('properties:owners-list')
		self.owners_details_url = reverse('properties:owners-details')
		self.bookings_list_url = reverse('properties:bookings-list')
		
		self.create_property_JSON = \
			{
				"title": "test_property_1",
				"body": "test_description_1",
				"price": 100,
				"property_type_id": 100,
				"property_address": [
					{
						"paddr_country": "Country_test_1",
						"paddr_city": "City_test_1",
						"paddr_street_1": "street_test_1",
						"paddr_street_2": "street_test_2",
						"paddr_building": "1",
						"paddr_floor": "1",
						"paddr_number": "1",
						"pzip_code": "100000"
					}
				]
			}
		self.correct_JSON_response_for_creation = \
			{
				"id": 1,
				"creator_id": 1,
				"title": "test_property_1",
				"body": "test_description_1",
				"property_type_id": 100,
				"price": 100,
				"active": True,
				"property_address": [
					{
						"paddr_country": "Country_test_1",
						"paddr_city": "City_test_1",
						"paddr_street_1": "street_test_1",
						"paddr_street_2": "street_test_2",
						"paddr_building": "1",
						"paddr_floor": "1",
						"paddr_number": "1",
						"pzip_code": "100000"
					}
				]
			}
		self.register_access_JSON = \
			{
				"client_first_name": "test_1_fname",
				"client_last_name": "test_1_sname",
				"client_patronymic": "test_1_pname",
				"client_email": "test1@test.com",
				"client_dob": "2000-01-01",
				"client_description": "some text",
				"access_start": "2020-12-07T14:34:37.318Z",
				"access_stop": "2020-12-07T14:34:37.318Z",
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

		self.response_post = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')

	def test_create_property(self):

		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.response_post.data["access"]}')
		resp = client.post(self.properties_list_url, self.create_property_JSON,
						format='json')

		ownership_obj = Ownership.objects.get(owner=self.correct_JSON_response_for_creation["creator_id"],
											premises=self.correct_JSON_response_for_creation["id"])
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		self.assertEqual(resp.data, self.correct_JSON_response_for_creation)

		self.assertEqual(self.registration_json_correct["first_name"], ownership_obj.owner.first_name)
		self.assertEqual(self.registration_json_correct["last_name"], ownership_obj.owner.last_name)
		self.assertEqual(self.registration_json_correct["email"], ownership_obj.owner.email)
		self.assertEqual(400, ownership_obj.permission_level_id)

		self.assertEqual(self.correct_JSON_response_for_creation["id"], ownership_obj.premises_id)
		self.assertEqual(self.correct_JSON_response_for_creation["title"], ownership_obj.premises.title)
		self.assertEqual(self.correct_JSON_response_for_creation["body"], ownership_obj.premises.body)
		self.assertEqual(self.correct_JSON_response_for_creation["creator_id"], ownership_obj.owner.id)

		created_property = Property.objects.get(pk=resp.data["id"])
		self.assertEqual(created_property.pk, resp.data["id"])
		self.assertEqual(created_property.title, resp.data["title"])
		self.assertEqual(created_property.body, resp.data["body"])
		self.assertEqual(created_property.price, resp.data["price"])
		self.assertEqual(created_property.visibility, 100)
		self.assertEqual(created_property.active, resp.data["active"])
		self.assertEqual(created_property.author.id, resp.data["creator_id"])

		created_address = PremisesAddresses.objects.get(premises=resp.data["id"])
		p_address = resp.data['property_address'][0]
		self.assertEqual(created_address.paddr_country, p_address["paddr_country"])
		self.assertEqual(created_address.paddr_city, p_address["paddr_city"])
		self.assertEqual(created_address.paddr_building, p_address["paddr_building"])
		self.assertEqual(created_address.paddr_street_1, p_address["paddr_street_1"])
		self.assertEqual(created_address.paddr_street_2, p_address["paddr_street_2"])
		self.assertEqual(created_address.paddr_floor, p_address["paddr_floor"])
		self.assertEqual(created_address.paddr_number, p_address["paddr_number"])
		self.assertEqual(created_address.pzip_code, p_address["pzip_code"])

	def test_update_property(self):
		pass

	def test_delete_property(self):
		pass

	def test_add_owners(self):
		pass

	def test_delete_owners(self):
		pass

	def test_update_owners(self):
		pass

	def test_add_one_image(self):
		pass

	def test_add_multiple_images(self):
		pass

	def test_delete_of_images(self):
		pass

	def test_add_lock(self):
		pass

	def test_delete_lock(self):
		pass

	def test_add_booking(self):
		pass

	def test_update_booking(self):
		pass

	def test_delete_booking(self):
		pass

