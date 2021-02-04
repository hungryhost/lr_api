from django.db import models
from phone_field import PhoneField
from django.conf import settings
# Create your models here.
from common.models import SupportedCity


class SupportMessage(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="support_messages",
		on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=255, null=False, blank=True)
	message = models.CharField(max_length=1000, null=False, blank=True)


class LockMessage(models.Model):
	email = models.EmailField(max_length=255, null=False, blank=True)
	fio = models.CharField(max_length=255, null=False, blank=False)
	phone = PhoneField(blank=True, help_text='Contact phone number')
	comment = models.CharField(max_length=500, null=False, blank=True)
	company = models.CharField(max_length=255, null=False, blank=True)
	quantity = models.IntegerField(default=1, null=False, blank=False)


class ShippingAddress(models.Model):
	r"""
	Model for storing address for shipping
	"""
	shipping_ticket = models.OneToOneField(LockMessage, related_name='shipping_address', on_delete=models.CASCADE,
									null=True, blank=True)
	country = models.CharField(max_length=100, blank=False, null=False)
	city = models.ForeignKey(SupportedCity, to_field='name', on_delete=models.CASCADE,
	                         related_name='shipping_city', blank=False, null=False)
	street = models.CharField(max_length=255, blank=False, null=False)
	building = models.CharField(max_length=20, blank=True, null=False)
	floor = models.CharField(max_length=20, blank=True, null=False)
	number = models.CharField(max_length=30, blank=True, null=False)
	zip_code = models.CharField(max_length=10, blank=True, null=False)
	directions_description = models.CharField(max_length=500, blank=True, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)
