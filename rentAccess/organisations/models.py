from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
# Create your models here.
from cities_light.models import City


class OrganisationPermissions(models.Model):
	r"""
	Model for permissions available for members of an organisation.
	Must be filled in manually on creation.
	"""
	codename = models.CharField(max_length=100, primary_key=True)
	description = models.CharField(max_length=255, null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.codename

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationPermissions, self).save(*args, **kwargs)


class Organisation(models.Model):

	name = models.CharField(max_length=255, null=False, blank=False)
	website = models.URLField(max_length=255, null=False, blank=True)
	description = models.TextField(max_length=500, null=False, blank=True)
	is_confirmed = models.BooleanField(default=False)
	active = models.BooleanField(default=True, null=False, blank=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		indexes = [
			models.Index(fields=['id']), ]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(Organisation, self).save(*args, **kwargs)


class OrganisationAddress(models.Model):
	organisation = models.OneToOneField(Organisation, related_name='organisation_address', on_delete=models.CASCADE,
		null=False, blank=False)
	country = CountryField()
	city = models.CharField(max_length=255, null=False, blank=False)
	street = models.CharField(max_length=255, blank=False, null=False)
	building = models.CharField(max_length=20, blank=True, null=False)
	floor = models.CharField(max_length=20, blank=True, null=False)
	number = models.CharField(max_length=30, blank=True, null=False)
	zip_code = models.CharField(max_length=10, blank=True, null=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationAddress, self).save(*args, **kwargs)
