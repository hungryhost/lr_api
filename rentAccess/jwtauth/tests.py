from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
import logging
User = get_user_model()



class TestsOfJWTUtils(APITestCase):
	r"""
	This is a utility class for the TestsOfJWT class.
	"""
	def test_auth_only_page(self, access_token):
		self.auth_only_url = reverse('userAccount:user-details')
		self.false_token = "adamantly"
		client = APIClient()
		client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.false_token}')
		resp = client.get(self.auth_only_url, data={'format': 'json'})
		self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
		client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
		resp = client.get(self.auth_only_url, data={'format': 'json'})
		self.assertEqual(resp.status_code, status.HTTP_200_OK)


class TestsOfJWT(APITestCase):
	r"""
	This class of tests is used for testing of the JWT authorization.
	What is covered in this test:
		- registration
		- login
		- logout
		- logout_all
	Note: since this API uses rest_framework_simplejwt we do not test the token
	issuing mechanism, i.e. refresh, verify, etc.
	"""

	def setUp(self) -> None:
		self.false_token = "adamantly"
		self.token_verify_url = reverse('jwtauth:token_verify')
		self.token_obtain_ulr = reverse('jwtauth:token_obtain_pair')
		self.registration_url = reverse('jwtauth:register')
		self.login_url = reverse('jwtauth:token_obtain_pair')
		self.logout_url = reverse('jwtauth:logout')
		self.logout_all_url = reverse('jwtauth:logout_all')

		# this section of JSON bodies for the requests
		self.login_body_correct = \
			{
				"email": "test_case_email@test.com",
				"password": "test_pass_test_pass"
			}
		self.login_body_incorrect_email = \
			{
				"email": "test_case_email1@test.com",
				"password": "test_pass_test_pass",
			}
		self.login_body_incorrect_pass = \
			{
				"email": "test_case_email@test.com",
				"password": "test_pass_test_pass1",
			}
		# this section of JSON bodies for the responses assertion
		self.registration_json_correct = \
			{
				"first_name": "test_case_fn",
				"last_name": "test_case_ln",
				"email": "test_case_email@test.com",
				"password": "test_pass_test_pass",
				"password2": "test_pass_test_pass"
			}
		# be advised: first account always creates with id of 1
		self.personal_info_correct = \
			{
				"id": 1,
				"username": "test_case_email_1",
				"email": "test_case_email@test.com",
				"userpic": "",
				"first_name": "test_case_fn",
				"last_name": "test_case_ln",
				"patronymic": "",
				"bio": "",
				"is_confirmed": False,
				"dob": "1970-01-01",
				"gender": "",
				"is_staff": False,
				"properties_url": "http://testserver/api/v1/user/1/properties/",
				"documents_url": "http://testserver/api/v1/user/1/documents/",
				"billing_addresses_url": "http://testserver/api/v1/user/1/billing_addresses/",
				"phones_url": "http://testserver/api/v1/user/1/phones/"
			}

	def test_registration(self):
		# client = APIClient()
		response_post = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')
		# the request below is expected to fail due to existence of the user
		# with the same credentials
		response_post_fail = self.client.post(
			path=self.registration_url,
			data=self.registration_json_correct,
			format='json')
		# user = User.objects.get(email="test_case_email@test.com")
		# assertion of the status codes
		self.assertEqual(response_post_fail.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
		# now we assert the data from the response
		personal_info = dict(response_post.data["personal_info"])

		personal_info.pop("last_updated")
		personal_info.pop("date_created")
		self.assertEqual(personal_info, self.personal_info_correct)

		# now we need to verify the token
		token = response_post.data["access"]
		response_verify = self.client.post(
			path=self.token_verify_url,
			data={"token": token},
			format='json'
		)
		self.assertEqual(response_verify.status_code, status.HTTP_200_OK)
		utils = TestsOfJWTUtils()
		utils.test_auth_only_page(access_token=token)

	def test_login(self):
		self.test_registration()

		response_post_correct = self.client.post(
			path=self.login_url,
			data=self.login_body_correct,
			format='json')
		token = response_post_correct.data["access"]
		self.assertEqual(response_post_correct.status_code, status.HTTP_200_OK)
		personal_info = dict(response_post_correct.data["personal_info"])

		personal_info.pop("last_updated")
		personal_info.pop("date_created")
		self.assertEqual(personal_info, self.personal_info_correct)

		response_post_fail_on_email = self.client.post(
			path=self.login_url,
			data=self.login_body_incorrect_email,
			format='json')
		self.assertEqual(response_post_fail_on_email.status_code, status.HTTP_400_BAD_REQUEST)

		response_post_fail_on_pass = self.client.post(
			path=self.login_url,
			data=self.login_body_incorrect_pass,
			format='json')
		self.assertEqual(response_post_fail_on_pass.status_code, status.HTTP_400_BAD_REQUEST)

		response_verify = self.client.post(
			path=self.token_verify_url,
			data={"token": token},
			format='json'
		)

		self.assertEqual(response_verify.status_code, status.HTTP_200_OK)
		# now let's test the access to auth-only page (main page of user)
		# note: this test does not check the content of the auth-only page
		utils = TestsOfJWTUtils()
		utils.test_auth_only_page(access_token=token)

	def test_logout(self):
		pass
		# self.assertEqual(resp.status_code, status.HTTP_205_RESET_CONTENT)
		# resp = client.post(self.logout_url, data=logout_body_incorrect)
		# self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
		# client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.false_token}')
		# resp = client.post(self.logout_url, data=logout_body_correct)
		# self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


