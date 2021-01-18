from api_tests.string_utils import generate_random_string
import random


class UserRegistrationJSON:
	def __init__(self):
		self._first_name = self._generate_valid_first_name()
		self._last_name = self._generate_valid_last_name()
		self._email = self._generate_valid_email()
		self._password1, self._password2 = self._generate_valid_passwords()

	@staticmethod
	def _generate_valid_first_name():
		return generate_random_string(random.randint(2, 10))

	@staticmethod
	def _generate_valid_last_name():
		return generate_random_string(random.randint(2, 20))

	@staticmethod
	def _generate_valid_email():
		email = generate_random_string(random.randint(2, 20))
		email = email + "@lockandrent.ru"
		return email

	@staticmethod
	def _generate_valid_passwords():
		password1 = password2 = generate_random_string(random.randint(8, 30))
		return password1, password2

	def get_request_json(self):
		json = \
			{
				"first_name": self._first_name,
				"last_name": self._last_name,
				"email": self._email,
				"password": self._password1,
				"password2": self._password2
			}
		return json
