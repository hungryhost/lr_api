from django.db import models
from properties.models import Property
import datetime
from django.conf import settings


class Bookings(models.Model):
	booked_from = models.DateTimeField(null=False, blank=False)
	booked_until = models.DateTimeField(null=False, blank=False)
	booked_property = models.ForeignKey(Property, related_name="bookings",
		on_delete=models.CASCADE, null=False, blank=False)
	price = models.IntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
	client_email = models.EmailField(null=False, blank=True)
	number_of_clients = models.IntegerField(null=False, blank=True, default=1)
	STATUS_CHOICES = [
		('ACCEPTED', 'Approved'),
		('AWAITING', 'Awaiting action from the owner'),
		('DECLINED', 'The owner declined the request')
	]
	status = models.CharField(max_length=100, choices=STATUS_CHOICES,
							null=False, blank=False, default='AWAITING')
	booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_by",
								on_delete=models.CASCADE, null=True, blank=True)

	is_deleted = models.BooleanField(default=False, null=False, blank=False)

	def __str__(self):
		return self.status + " " + "client: " + self.client_email + " from: " + str(self.booked_from.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)) \
			+ " Until: " + str(self.booked_until.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None))