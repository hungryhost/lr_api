import datetime
import random
import string
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from common.models import PermissionLevels
from .models import PropertyTypes, Ownership, Property, PremisesAddresses, PremisesImages

User = get_user_model()


def generate_random_string(length=10):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))


def generate_random_list_of_strings(size=5, length=10):
	list_of_strings = []
	for i in range(size):
		list_of_strings.append(generate_random_string(length))
	return list_of_strings


def generate_random_list_of_numbers(size=5, a=100, b=99999):
	list_of_numbers = []
	for i in range(size):
		list_of_numbers.append(random.randint(a, b))
	return list_of_numbers


def generate_list_of_images():
	image1 = Image.new('RGB', (100, 100))
	image2 = Image.new('RGB', (100, 100))
	image3 = Image.new('RGB', (100, 100))
	image4 = Image.new('RGB', (100, 100))
	image5 = Image.new('RGB', (100, 100))
	image6 = Image.new('RGB', (100, 100))

	tmp_file1 = tempfile.NamedTemporaryFile(suffix='.jpg')
	tmp_file2 = tempfile.NamedTemporaryFile(suffix='.png')
	tmp_file3 = tempfile.NamedTemporaryFile(suffix='.jpg')
	tmp_file4 = tempfile.NamedTemporaryFile(suffix='.png')
	tmp_file5 = tempfile.NamedTemporaryFile(suffix='.jpg')
	tmp_file6 = tempfile.NamedTemporaryFile(suffix='.png')
	image1.save(tmp_file1)
	image2.save(tmp_file2)
	image3.save(tmp_file3)
	image4.save(tmp_file4)
	image5.save(tmp_file5)
	image6.save(tmp_file6)

	tmp_file1.seek(0)
	tmp_file2.seek(0)
	tmp_file3.seek(0)
	tmp_file4.seek(0)
	tmp_file5.seek(0)
	tmp_file6.seek(0)

	images = [
		tmp_file1,
		tmp_file2,
		tmp_file3,
		tmp_file4,
		tmp_file5,
		tmp_file6
	]
	return images


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

		self.false_token = "adamantly"

		self.token_verify_url = reverse('jwtauth:token_verify')
		self.token_obtain_ulr = reverse('jwtauth:token_obtain_pair')
		self.registration_url = reverse('jwtauth:register')
		self.login_url = reverse('jwtauth:token_obtain_pair')
		self.logout_url = reverse('jwtauth:logout')
		self.logout_all_url = reverse('jwtauth:logout_all')
		self.address_attr = [
			"paddr_country",
			"paddr_city",
			"paddr_street_1",
			"paddr_street_2",
			"paddr_building",
			"paddr_floor",
			"paddr_number",
			"pzip_code"
		]
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
		self.properties_list_url = reverse('properties:properties-list')
		self.owners_list_url = reverse('properties:owners-list', args=[self.correct_JSON_response_for_creation["id"]])
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
				"title": list_of_titles[random.randint(0, len(list_of_titles)-1)],
				"body": list_of_descriptions[random.randint(0, len(list_of_descriptions)-1)],
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
			if item not in ['pzip_code', 'paddr_building', 'paddr_floor', 'paddr_number']:
				data = {
					item: generate_random_string()
				}
			else:
				if item == 'pzip_code':
					data = {
						item: str(random.randint(100000, 999999))
					}
				if item == 'paddr_building':
					data = {
						item: str(random.randint(1, 99))
					}
				if item == 'paddr_floor':
					data = {
						item: str(random.randint(1, 99))
					}
				if item == 'paddr_number':
					data = {
						item: str(random.randint(1, 9999))
					}
			request_data = {
				"property_address": [data]
			}
			resp_auth = self.client.patch(new_property_details_url,
										data=request_data, format='json')
			resp_auth.data.pop('created_at')
			resp_auth.data.pop('updated_at')

			p_address = resp_auth.data['property_address'][0]
			self.assertEqual(data[item], p_address[item])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)
		data_for_update_of_address = \
			{
				"property_address": [
					{
						"paddr_country": generate_random_string(),
						"paddr_city": generate_random_string(),
						"paddr_street_1": generate_random_string(),
						"paddr_street_2": generate_random_string(),
						"paddr_building": str(random.randint(1, 99)),
						"paddr_floor": str(random.randint(1, 99)),
						"paddr_number": str(random.randint(1, 9999)),
						"pzip_code": str(random.randint(100000, 999999))
					}
				]
			}
		data_for_update_of_address["property_address"][0].pop(self.address_attr[random.randint(1, 2)])
		data_for_update_of_address["property_address"][0].pop(self.address_attr[random.randint(3, 6)])
		resp_auth = self.client.patch(new_property_details_url,
									data=data_for_update_of_address, format='json')
		resp_auth.data.pop('created_at')
		resp_auth.data.pop('updated_at')
		self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		created_address = PremisesAddresses.objects.get(premises=resp_auth.data["id"])
		p_address = resp_auth.data['property_address'][0]
		self.assertEqual(created_address.paddr_country, p_address["paddr_country"])
		self.assertEqual(created_address.paddr_city, p_address["paddr_city"])
		self.assertEqual(created_address.paddr_building, p_address["paddr_building"])
		self.assertEqual(created_address.paddr_street_1, p_address["paddr_street_1"])
		self.assertEqual(created_address.paddr_street_2, p_address["paddr_street_2"])
		self.assertEqual(created_address.paddr_floor, p_address["paddr_floor"])
		self.assertEqual(created_address.paddr_number, p_address["paddr_number"])
		self.assertEqual(created_address.pzip_code, p_address["pzip_code"])

		created_property = Property.objects.get(pk=resp_auth.data["id"])
		self.assertEqual(created_property.pk, resp_auth.data["id"])
		self.assertEqual(created_property.title, resp_auth.data["title"])
		self.assertEqual(created_property.body, resp_auth.data["body"])
		self.assertEqual(created_property.price, resp_auth.data["price"])
		self.assertEqual(created_property.visibility, 100)
		self.assertEqual(created_property.active, resp_auth.data["active"])
		self.assertEqual(created_property.author.id, resp_auth.data["creator_id"])

	def test_delete_property(self):
		pass

	def test_add_images(self):
		resp_post = self.client.post(self.properties_list_url, self.create_property_JSON,
									format='json')
		images = generate_list_of_images()
		resp_auth_1 = self.client.put(reverse('properties:properties-images-list', args=(resp_post.data["id"], )),
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
		resp_get = self.client.get(reverse('properties:properties-details', args=(resp_post.data["id"],)),
								format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		self.assertIsNot(resp_get.data["property_images"], [])
		iterator = 2
		for item in resp_get.data["property_images"]:
			self.assertEqual(len(resp_get.data["property_images"]), PremisesImages.objects.filter(premises_id=resp_post.data["id"]).count()-1)
			self.assertEqual(item["id"], iterator)
			self.assertIsNot(item["image"], "")
			iterator += 1
		obj = PremisesImages.objects.get(premises_id=resp_post.data["id"], is_main=True)
		self.assertEqual(obj.pk, 1)

	def test_change_main_image(self):
		resp_post = self.client.post(self.properties_list_url, self.create_property_JSON,
									format='json')
		resp_auth_1 = self.client.put(reverse('properties:properties-main-image-setter', args=(resp_post.data["id"],))
									, data={"image_id":1}, format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_404_NOT_FOUND)
		images = generate_list_of_images()
		resp_auth_1 = self.client.put(reverse('properties:properties-images-list', args=(resp_post.data["id"],)),
									data={
										'images': [
											images[0],
											images[1],
											images[2],
											images[3],
											images[4],
											images[5],
										],

									},format='multipart')

		resp_auth_1 = self.client.put(reverse('properties:properties-main-image-setter', args=(resp_post.data["id"],)),
									data={"image_id": 3}, format='json')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		resp_get = self.client.get(reverse('properties:properties-details', args=(resp_post.data["id"],)),
								format='json')

		for item in resp_get.data["property_images"]:
			self.assertEqual(len(resp_get.data["property_images"]),
							PremisesImages.objects.filter(premises_id=resp_post.data["id"]).count() - 1)
			self.assertIsNot(item["id"], 3)

	def test_delete_images(self):
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

	def test_add_booking(self):
		pass

	def test_update_booking(self):
		pass

	def test_delete_booking(self):
		pass

	def test_visibility(self):
		pass
