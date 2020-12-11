import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
import random
import string
from itertools import product
User = get_user_model()


def generate_random_string(length=10):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))


def generate_random_list_of_strings(size=5, length=10):
	list_of_strings = []
	for i in range(size):
		list_of_strings.append(generate_random_string(length))
	return list_of_strings


class OwnerUserAccountTest(APITestCase):
	r"""
	This class of tests is used for testing of following endpoints:
		- Access to account's main page
		- Partial Update of the account
		- Create/Update/Delete of the user's own userpic
		- Create/Update/Delete of the user's own documents
		- Create/Update/Delete of the user's own billing addresses
		- Create/Update/Delete the user's own of phones
		- Changing of user's own password
		- !!Deprecated: Changing of user's own username
		- Tests of permissions
		- Tests of access to another user's info
		- Access to sub-resources like properties, etc.
	"""

	def setUp(self) -> None:
		self.false_token = "adamantly"
		self.token_verify_url = reverse('jwtauth:token_verify')
		self.token_obtain_ulr = reverse('jwtauth:token_obtain_pair')
		self.registration_url = reverse('jwtauth:register')
		self.login_url = reverse('jwtauth:token_obtain_pair')
		self.logout_url = reverse('jwtauth:logout')
		self.logout_all_url = reverse('jwtauth:logout_all')
		self.properties_create_list_url = reverse('properties:property-list')
		self.user_main_page_url = reverse('userAccount:user-details')
		self.userpic_url = reverse('userAccount:userpic')
		# this section of JSON bodies for the requests
		self.registration_json_correct = \
			{
				"first_name": "test_case_fn",
				"last_name": "test_case_ln",
				"email": "test_case_email@test.com",
				"password": "test_pass_test_pass",
				"password2": "test_pass_test_pass"
			}
		# this section of JSON bodies for the responses assertion
		# be advised: first account always creates with id of 1
		self.main_page_payload_JSON = \
			{
				"id": 1,
				"username": "test_case_email_1",
				"email": "test_case_email@test.com",
				"userpic": "",
				"first_name": "test_case_fn",
				"last_name": "test_case_ln",
				"patronymic": "",
				"bio": "",
				"account_type": "OWNER",
				"is_confirmed": False,
				"dob": "1970-01-01",
				"gender": "",
				"properties_url": "http://testserver/api/v1/user/1/properties/",
				"documents_url": "http://testserver/api/v1/user/1/documents/",
				"billing_addresses_url": "http://testserver/api/v1/user/1/billing_addresses/",
				"phones_url": "http://testserver/api/v1/user/1/phones/",
			}

		self.list_of_possible_genders = [
			'M',
			'F',
			'D'
		]
		self.list_of_possible_dobs = [
			'2000-01-01',
			'2002-01-01',
			'01-01-2000',
		]

		self.response_post = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')
		self.client_auth = APIClient()
		self.client_not_auth = APIClient()
		self.client_auth.credentials(HTTP_AUTHORIZATION=f'Bearer {self.response_post.data["access"]}')

	def test_main_page_access(self):
		resp_auth = self.client_auth.get(self.user_main_page_url, format='json')
		# due to the fact that we can't really test the dates for updating and
		# creating the object, we must pop them from data and then compare
		resp_auth.data.pop('date_created')
		resp_auth.data.pop('last_updated')
		self.assertEqual(resp_auth.data, self.main_page_payload_JSON)
		self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)
		resp_not_auth = self.client_not_auth.get(self.user_main_page_url, format='json')
		self.assertEqual(resp_not_auth.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_partial_update(self):
		list_of_first_names = generate_random_list_of_strings(10, 7)
		list_of_last_names = generate_random_list_of_strings(10, 10)
		list_of_patronymics = generate_random_list_of_strings(10, 10)
		list_of_random_bios = generate_random_list_of_strings(10, 50)

		for i in range(len(list_of_first_names)):
			data = {"first_name": list_of_first_names[i]}
			resp_auth = self.client_auth.patch(self.user_main_page_url,
											data=data, format='json')
			resp_auth.data.pop('date_created')
			resp_auth.data.pop('last_updated')
			self.assertEqual(resp_auth.data["first_name"], list_of_first_names[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)
		for i in range(len(list_of_last_names)):
			data = {"last_name": list_of_last_names[i]}
			resp_auth = self.client_auth.patch(self.user_main_page_url,
											data=data, format='json')
			resp_auth.data.pop('date_created')
			resp_auth.data.pop('last_updated')
			self.assertEqual(resp_auth.data["last_name"], list_of_last_names[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(list_of_patronymics)):
			data = {"patronymic": list_of_patronymics[i]}
			resp_auth = self.client_auth.patch(self.user_main_page_url,
											data=data, format='json')
			resp_auth.data.pop('date_created')
			resp_auth.data.pop('last_updated')
			self.assertEqual(resp_auth.data["patronymic"], list_of_patronymics[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)
		for i in range(len(list_of_random_bios)):
			data = {"bio": list_of_random_bios[i]}
			resp_auth = self.client_auth.patch(self.user_main_page_url,
											data=data, format='json')
			resp_auth.data.pop('date_created')
			resp_auth.data.pop('last_updated')
			self.assertEqual(resp_auth.data["bio"], list_of_random_bios[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(self.list_of_possible_genders)-1):
			data = {"gender": self.list_of_possible_genders[i]}
			resp_auth = self.client_auth.patch(self.user_main_page_url,
											data=data, format='json')
			resp_auth.data.pop('date_created')
			resp_auth.data.pop('last_updated')
			self.assertEqual(resp_auth.data["gender"], self.list_of_possible_genders[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		for i in range(len(self.list_of_possible_dobs)-1):
			data = {"dob": self.list_of_possible_dobs[i]}
			resp_auth = self.client_auth.patch(self.user_main_page_url,
											data=data, format='json')
			resp_auth.data.pop('date_created')
			resp_auth.data.pop('last_updated')
			self.assertEqual(resp_auth.data["dob"], self.list_of_possible_dobs[i])
			self.assertEqual(resp_auth.status_code, status.HTTP_200_OK)

		data = {"gender": self.list_of_possible_genders[len(self.list_of_possible_genders) - 1]}
		resp_auth = self.client_auth.patch(self.user_main_page_url,
										   data=data, format='json')
		resp_auth.data.pop('date_created')
		resp_auth.data.pop('last_updated')
		self.assertEqual(resp_auth.data["gender"], self.list_of_possible_genders[len(self.list_of_possible_genders) - 2])

		data = {"dob": self.list_of_possible_dobs[len(self.list_of_possible_dobs) - 1]}
		resp_auth = self.client_auth.patch(self.user_main_page_url,
										   data=data, format='json')
		self.assertEqual(resp_auth.status_code, status.HTTP_400_BAD_REQUEST)

	def test_upload_update_userpic(self):
		image1 = Image.new('RGB', (100, 100))
		image2 = Image.new('RGB', (100, 100))

		tmp_file1 = tempfile.NamedTemporaryFile(suffix='.jpg')
		tmp_file2 = tempfile.NamedTemporaryFile(suffix='.png')
		image1.save(tmp_file1)
		image2.save(tmp_file2)
		tmp_file1.seek(0)

		resp_auth_1 = self.client_auth.put(self.userpic_url,
										   data={
											   'image': tmp_file1
										   }, format='multipart')
		self.assertEqual(resp_auth_1.status_code, status.HTTP_200_OK)
		self.assertIsNot(resp_auth_1.data['image'], "")
		tmp_file2.seek(0)
		resp_auth_2 = self.client_auth.put(self.userpic_url,
										 data={
											 'image': tmp_file2
										 }, format='multipart')

		self.assertEqual(resp_auth_2.status_code, status.HTTP_200_OK)
		self.assertIsNot(resp_auth_2.data['image'], "")
		self.assertNotEqual(resp_auth_1.data['image'], resp_auth_2.data['image'])

	def test_delete_userpic(self):
		pass

	def test_access_to_documents(self):
		pass

	def test_create_document(self):
		pass

	def test_delete_document(self):
		pass

	def test_update_documents(self):
		pass

	def test_access_to_billing_addresses(self):
		pass

	def test_create_billing_addresses(self):
		pass

	def test_delete_billing_addresses(self):
		pass

	def test_update_billing_addresses(self):
		pass

	def test_access_to_phones(self):
		pass

	def test_create_phones(self):
		pass

	def test_delete_phones(self):
		pass

	def test_update_phones(self):
		pass

	def test_change_password(self):
		pass

class ClientUserAccountAccessTest(APITestCase):
	r"""
	This class of tests is used for testing of following endpoints:
		- Access some user's info
	"""
	pass


class AdminUserAccountTest(APITestCase):
	r"""
	This class of tests is used for testing of following endpoints:
		- Admin access to user's profile
		- Deleting a user
		- Deleting user's resources
		- Granting/Revoking user's admin permissions
		- Approving user and user's resources in various situations
	"""
