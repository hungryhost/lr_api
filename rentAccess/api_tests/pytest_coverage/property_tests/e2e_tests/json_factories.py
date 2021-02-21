from properties.availability_utils import available_days_from_db


class PropertyJsonFactory:

	def __init__(self, _property):
		self._property = _property

	def address_to_json(self):
		json = {
			"country": self._property.property_address.country,
			"city": self._property.property_address.city.name,
			"street": self._property.property_address.street,
			"building": self._property.property_address.building,
			"floor": self._property.property_address.floor,
			"number": self._property.property_address.number,
			"zip_code": self._property.property_address.zip_code,
			"directions_description": self._property.property_address.directions_description
		}
		return json

	def property_to_json(self):
		json = {
			"title": self._property.title,
			"body": self._property.body,
			"price": self._property.price,
			"booking_type": self._property.booking_type,
			"visibility": self._property.visibility,
			"property_type": self._property.property_type.pk,
			"client_greeting_message": self._property.client_greeting_message,
			"requires_additional_confirmation": self._property.requires_additional_confirmation,
		}
		return json

	def availability_to_json(self):
		if self._property.booking_type == 200:

			json = {
				"open_days": available_days_from_db(self._property.availability.open_days),
				"available_until": self._property.availability.available_until.strftime("%H:%M"),
				"available_from": self._property.availability.available_from.strftime("%H:%M"),
				"maximum_number_of_clients": self._property.availability.maximum_number_of_clients
			}
		else:
			json = {
				"open_days": available_days_from_db(self._property.availability.open_days),
				"arrival_time_from": self._property.availability.available_from.strftime("%H:%M"),
				"departure_time_until": self._property.availability.available_until.strftime("%H:%M"),
				"maximum_number_of_clients": self._property.availability.maximum_number_of_clients
			}
		return json

	def dump_json(self):
		json = self.property_to_json()
		json['availability'] = self.availability_to_json()
		json['property_address'] = self.address_to_json()
		return json