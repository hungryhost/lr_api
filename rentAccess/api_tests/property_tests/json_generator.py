from api_tests.string_utils import generate_random_string
import random


class AddressJson:
	r"""
	Generates address dict for property.

	"""
	def __init__(
			self,
			invalid_params: list = None
		):
		r"""
		No parameters required by default.

		:type invalid_params: list
		:param invalid_params: list of address fields that should be generated as invalid.

		:rtype: AddressJson
		"""
		self._invalid_params = invalid_params
		self._country = "Russia"
		self._city = "Moscow"

		if self._invalid_params and "street_1" in self._invalid_params:
			self._street_1 = self._generate_invalid_street_1()
		else:
			self._street_1 = self._generate_valid_street_1()

		if self._invalid_params and "street_2" in self._invalid_params:
			self._street_2 = self._generate_invalid_street_2()
		else:
			self._street_2 = self._generate_valid_street_2()

		if self._invalid_params and "building" in self._invalid_params:
			self._building = self._generate_invalid_building()
		else:
			self._building = self._generate_valid_building()

		if self._invalid_params and "floor" in self._invalid_params:
			self._floor = self._generate_invalid_floor()
		else:
			self._floor = self._generate_valid_floor()

		if self._invalid_params and "number" in self._invalid_params:
			self._number = self._generate_invalid_number()
		else:
			self._number = self._generate_valid_number()

		if self._invalid_params and "zip_code" in self._invalid_params:
			self._zip_code = self._generate_invalid_zip_code()
		else:
			self._zip_code = self._generate_valid_zip_code()

		if self._invalid_params and "directions_description" in self._invalid_params:
			self._directions_description = self._generate_invalid_directions_description()
		else:
			self._directions_description = self._generate_valid_directions_description()

	@staticmethod
	def _generate_valid_street_1():
		return generate_random_string(random.randint(10, 100))

	@staticmethod
	def _generate_valid_street_2():
		return generate_random_string(random.randint(10, 100))

	@staticmethod
	def _generate_valid_building():
		return str(random.randint(1, 99))

	@staticmethod
	def _generate_valid_floor():
		return str(random.randint(1, 150))

	@staticmethod
	def _generate_valid_number():
		return str(random.randint(1, 10000))

	@staticmethod
	def _generate_valid_directions_description():
		return generate_random_string(random.randint(1, 500))

	@staticmethod
	def _generate_valid_zip_code():
		return str(random.randint(111111, 999999))

	@staticmethod
	def _generate_invalid_street_1():
		return generate_random_string(random.randint(101, 1000))

	@staticmethod
	def _generate_invalid_street_2():
		return generate_random_string(random.randint(101, 1000))

	@staticmethod
	def _generate_invalid_building():
		return str(random.randint(100, 1000))

	@staticmethod
	def _generate_invalid_floor():
		return str(random.randint(151, 550))

	@staticmethod
	def _generate_invalid_number():
		return str(random.randint(10000, 100000))

	@staticmethod
	def _generate_invalid_directions_description():
		return generate_random_string(random.randint(501, 1500))

	@staticmethod
	def _generate_invalid_zip_code():
		return str(random.randint(1, 1000))

	def get_address_json(self):
		json = {
			"country": self._country,
			"city": self._city,
			"street_1": self._street_1,
			"street_2": self._street_2,
			"building": self._building,
			"floor": self._floor,
			"number": self._number,
			"zip_code": self._zip_code,
			"directions_description": self._directions_description
		}
		return json


class PropertyJson:
	r"""
	Generates JSON bodies for properties.
	Note that the objects of this class DO NOT include property_address key.

	In order to generate invalid request body invalid_property_params must be specified.
	For validation info pls refer to serializers and their validators.
	"""
	def __init__(
			self,
			creator_id,
			invalid_property_params: list = None,
			requires_additional_confirmation: bool = False,
			booking_interval: int = 0,
			maximum_number_of_bookings_daily: int = -1,
			maximum_booking_length: int =- 1,
	):
		r"""

		:type visibility: int
		:type price: int
		:type property_type: int
		:type creator_id: int
		:param invalid_property_params: whether the json should be valid (for validation test).
		:param requires_additional_confirmation: whether the property requires confirmation for booking.
		:param booking_interval: the interval between bookings.
		:param maximum_number_of_bookings_daily: maximum number of bookings per day.
		:param maximum_booking_length: maximum length of bookings in minutes.
		:param creator_id: id of the user who makes the request.
		:param property_type: numeric id of property type (e.g. 100).
		:param price: price for the property per hour.
		:param visibility: numeric id of visibility (e.g. 100).
		:rtype: PropertyJson
		"""
		self._invalid_property_params = invalid_property_params
		self._creator_id = creator_id
		self._active = True
		self._main_image = ""
		self._visibility_list = [100, 200, 300]
		self._property_types = [100, 200]
		self._bookings_types = [100, 200]
		self._requires_additional_confirmation = requires_additional_confirmation
		self._maximum_booking_length = maximum_booking_length
		self._maximum_number_of_bookings_daily = maximum_number_of_bookings_daily
		self._booking_interval = booking_interval

		if self._invalid_property_params and "title" in self._invalid_property_params:
			self._title = self._generate_invalid_title()
		else:
			self._title = self._generate_valid_title()

		if self._invalid_property_params and "booking_type" in self._invalid_property_params:
			self._booking_type = self._generate_invalid_booking_type()
		else:
			self._booking_type = self._generate_valid_booking_type()

		if self._invalid_property_params and "body" in self._invalid_property_params:
			self._body = self._generate_invalid_body()
		else:
			self._body = self._generate_valid_body()

		if self._invalid_property_params and "price" in self._invalid_property_params:
			self._price = self._generate_invalid_price()
		else:
			self._price = self._generate_valid_price()

		if self._invalid_property_params and "property_type" in self._invalid_property_params:
			self._property_type = self._generate_invalid_type()
		else:
			self._property_type = self._generate_valid_type()

		if self._invalid_property_params and "client_greeting_message" in self._invalid_property_params:
			self._client_greeting_message = self._generate_invalid_greeting_message()
		else:
			self._client_greeting_message = self._generate_valid_greeting_message()

		if self._invalid_property_params and "visibility" in self._invalid_property_params:
			self._visibility = self._generate_invalid_visibility()
		else:
			self._visibility = self._generate_valid_visibility()

	@staticmethod
	def _generate_valid_title():
		return generate_random_string(random.randint(1, 50))

	@staticmethod
	def _generate_invalid_title():
		return generate_random_string(random.randint(51, 1000))

	@staticmethod
	def _generate_valid_body():
		return generate_random_string(random.randint(1, 500))

	@staticmethod
	def _generate_invalid_body():
		return generate_random_string(random.randint(501, 1500))

	@staticmethod
	def _generate_valid_greeting_message():
		return generate_random_string(random.randint(1, 500))

	@staticmethod
	def _generate_invalid_greeting_message():
		return generate_random_string(random.randint(501, 1500))

	@staticmethod
	def _generate_valid_price():
		return random.randint(1, 99999)

	def _generate_valid_visibility(self):
		choice = random.randint(1, 3)
		return self._visibility_list[choice-1]

	def _generate_valid_booking_type(self):
		choice = random.randint(1, 3)
		return self._bookings_types[choice - 1]

	def _generate_valid_type(self):
		choice = random.randint(1, 2)
		return self._property_types[choice-1]

	@staticmethod
	def _generate_invalid_price():
		return random.randint(100000, 1000000)

	@staticmethod
	def _generate_invalid_visibility():
		return random.randint(400, 600)

	@staticmethod
	def _generate_invalid_type():
		return random.randint(300, 600)

	@staticmethod
	def _generate_invalid_booking_type():
		return random.randint(300, 600)

	def _generate_request_json(
			self,
			include_greeting: bool = False,
			include_additional_conf: bool = False,
			include_interval: bool = False,
			include_maximum_number_of_bookings_daily: bool = False,
			include_maximum_booking_length: bool = False
	):
		"""
		Generates JSON-like dict for POST requests.

		:param include_greeting: whether to include greeting_message in JSON.
		:param include_additional_conf: whether to include additional confirmation in JSON
		:param include_interval: whether to include interval between bookings in JSON.
		:param include_maximum_number_of_bookings_daily: whether to include max number of bookings per day.
		:param include_maximum_booking_length: whether to include max length of bookings in minutes per day.
		:rtype: dict
		:return: dictionary for creation of a property.
		"""
		json = {
			"title": self._title,
			"body": self._body,
			"price": self._price,
			"visibility": self._visibility,
			"property_type": self._property_type,
			"client_greeting_message": self._client_greeting_message,
			"requires_additional_confirmation": self._requires_additional_confirmation,
			"booking_interval": self._booking_interval,
			"max_number_of_bookings_daily": self._maximum_number_of_bookings_daily,
			"max_booking_length": self._maximum_booking_length
		}
		if not include_greeting:
			json.pop("client_greeting_message")
		if not include_additional_conf:
			json.pop("requires_additional_confirmation")
		if not include_interval:
			json.pop("booking_interval")
		if not include_maximum_number_of_bookings_daily:
			json.pop("max_number_of_bookings_daily")
		if not include_maximum_booking_length:
			json.pop("max_booking_length")
		return json

	def _generate_response_json(self):

		json = {
			"creator_id": self._creator_id,
			"title": self._title,
			"body": self._body,
			"property_type": self._property_type,
			"visibility": self._visibility,
			"main_image": self._main_image,
			"price": self._price,
			"active": self._active,
			"client_greeting_message": self._client_greeting_message,
			"requires_additional_confirmation": self._requires_additional_confirmation
		}
		return json

	def get_request_json(self):
		return self._generate_request_json()

	def get_response_json(self):
		return self._generate_response_json()
