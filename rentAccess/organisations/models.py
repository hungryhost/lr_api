from django.conf import settings
from django.db import models
from django.utils import timezone
from django_countries.fields import CountryField
# Create your models here.
from cities_light.models import City
from rest_framework_api_key.models import AbstractAPIKey
from properties.models import Property


class Organisation(models.Model):
	name = models.CharField(max_length=255, null=False, blank=False)
	website = models.URLField(max_length=255, null=False, blank=True)
	description = models.CharField(max_length=500, null=False, blank=True)
	is_confirmed = models.BooleanField(default=False)
	active = models.BooleanField(default=True, null=False, blank=False)
	LR_CRM_ID = models.TextField(null=False, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'organisations'

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(Organisation, self).save(*args, **kwargs)


class OrganisationAPIKey(AbstractAPIKey):
	organisation = models.ForeignKey(
		Organisation,
		on_delete=models.CASCADE,
		related_name="api_keys",
	)


class OrganisationAddress(models.Model):
	class Meta:
		db_table = 'organisation_addresses'

	organisation = models.OneToOneField(Organisation, related_name='organisation_address', on_delete=models.CASCADE,
	                                    null=False, blank=False)
	country = CountryField()
	city = models.CharField(max_length=255, null=False, blank=False)
	street = models.CharField(max_length=255, blank=False, null=False)
	building = models.CharField(max_length=20, blank=True, null=False)
	floor = models.CharField(max_length=20, blank=True, null=False)
	number = models.CharField(max_length=30, blank=True, null=False)
	zip_code = models.CharField(max_length=10, blank=True, null=False)
	CRM_REGION = models.CharField(max_length=3, blank=True, null=False, default='R01')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationAddress, self).save(*args, **kwargs)


class OrganisationMember(models.Model):
	class Meta:
		unique_together = [['organisation', 'user']]
		db_table = 'organisation_members'

	organisation = models.ForeignKey(
		Organisation, null=False, related_name='member_tied_org', on_delete=models.CASCADE
	)
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL, related_name='user_orgs', on_delete=models.SET_NULL,
		null=True
	)
	is_creator = models.BooleanField(default=False, null=False)
	can_add_properties = models.BooleanField(default=False, null=False)
	can_delete_properties = models.BooleanField(default=False, null=False)
	can_book_properties = models.BooleanField(default=True, null=False)
	recursive_ownership = models.BooleanField(default=False, null=False)
	can_add_members = models.BooleanField(default=False, null=False)
	can_remove_members = models.BooleanField(default=False, null=False)
	can_manage_members = models.BooleanField(default=False, null=False)
	joined_with_code = models.BooleanField(default=False, null=False)
	joined_with_link = models.BooleanField(default=False, null=False)
	added_by_user_id = models.IntegerField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationMember, self).save(*args, **kwargs)


class OrganisationInviteLinks(models.Model):
	class Meta:
		db_table = 'organisation_invite_links'

	organisation = models.ForeignKey(
		Organisation,
		on_delete=models.CASCADE,
		related_name="invite_links",
	)
	secret_link = models.TextField(null=False, blank=False)
	expires_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	created_by_member = models.ForeignKey(
		OrganisationMember,
		on_delete=models.CASCADE,
		related_name="member_invite_links",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationInviteLinks, self).save(*args, **kwargs)


class OrganisationInviteCodes(models.Model):
	class Meta:
		db_table = 'organisation_invite_codes'

	organisation = models.ForeignKey(
		Organisation,
		on_delete=models.CASCADE,
		related_name="invite_codes",
	)
	secret_code = models.TextField(null=False, blank=False)
	expires_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	created_by_member = models.ForeignKey(
		OrganisationMember,
		on_delete=models.CASCADE,
		related_name="member_invite_codes",
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now_add=True)

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationInviteCodes, self).save(*args, **kwargs)


class OrganisationProperty(models.Model):
	class Meta:
		unique_together = [['premises', 'organisation']]
		db_table = 'organisation_properties'

	premises = models.ForeignKey(
		Property,
		related_name='mem_org',
		on_delete=models.CASCADE,
		null=False,
		blank=False
	)
	organisation = models.ForeignKey(
		Organisation,
		related_name='mem_property_org',
		on_delete=models.CASCADE,
		null=False,
		blank=False
	)
	added_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='org_added_properties',
		on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

	def save(self, *args, **kwargs):
		self.updated_at = timezone.now()
		super(OrganisationProperty, self).save(*args, **kwargs)

	def __str__(self):
		return self.premises.title + " in " + self.organisation.name
