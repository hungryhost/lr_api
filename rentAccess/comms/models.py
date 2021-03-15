from django.db import models
from phone_field import PhoneField
from django.conf import settings
# Create your models here.
from common.models import SupportedCity


class LockCatalogInfo(models.Model):
	name = models.CharField(max_length=500, null=False, blank=True)
	description = models.CharField(max_length=3000, null=False, blank=True)
	price = models.FloatField(null=False, blank=True)
	delivery = models.BooleanField(null=False, default=True)
	installation_included = models.BooleanField(null=False, default=True)
	is_available = models.BooleanField(null=False, default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)


class LockCatalogImages(models.Model):
	lock_info = models.ForeignKey(LockCatalogInfo, related_name='catalog_images', on_delete=models.CASCADE)
	image = models.ImageField()
	is_main = models.BooleanField(default=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)


class LockAvailabilityStorage(models.Model):
	lock_info = models.ForeignKey(LockCatalogInfo, related_name='lock_availability',
	                              on_delete=models.CASCADE)
	quantity = models.IntegerField(null=False, blank=False)
	city = models.ForeignKey(SupportedCity, to_field='name', on_delete=models.CASCADE,
	                         related_name='awailable_locks', blank=False, null=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)


class SupportMessage(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="support_messages",
	                         on_delete=models.CASCADE, null=True, blank=True)
	title = models.CharField(max_length=255, null=False, blank=True)
	message = models.CharField(max_length=1000, null=False, blank=True)


class LockMessage(models.Model):
	CHOICES = [
		('OK', 'Approved'),
		('FAIL', 'Rejected'),
		('WAIT', 'Await')
	]
	email = models.EmailField(max_length=255, null=False, blank=True)
	fio = models.CharField(max_length=255, null=False, blank=False)
	selected_lock = models.ForeignKey(LockCatalogInfo, null=True, blank=True,
	                                  on_delete=models.CASCADE)
	phone = PhoneField(blank=True, help_text='Contact phone number')
	status = models.CharField(max_length=20, null=False, blank=False, default='WAIT', choices=CHOICES)
	comment = models.CharField(max_length=500, null=False, blank=True)
	company = models.CharField(max_length=255, null=False, blank=True)
	quantity = models.IntegerField(default=1, null=False, blank=False)
	final_price = models.FloatField(null=True, blank=True)


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
