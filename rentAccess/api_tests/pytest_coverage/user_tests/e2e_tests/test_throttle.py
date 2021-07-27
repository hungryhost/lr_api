from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from api_tests.pytest_coverage.user_tests.factories import UserFactory
import pytest


@pytest.mark.throttle_tests
class ThrottleApiTests(APITestCase):

	def test_check_health(self):
		user = UserFactory()
		client = APIClient()
		_url = reverse('jwtauth:token_obtain_pair')
		_json = {
			"email"   : user.email,
			"password": "a123141"
		}
		for i in range(0, 5):
			client.post(
				_url,
				data=_json,
				format='json'
			)

		# this call should err
		response = client.post(
			_url,
			data=_json,
			format='json'
		)
		# 429 - too many requests
		self.assertEqual(response.status_code, 429)
