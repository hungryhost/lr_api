from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import os
from uuid import uuid4
from timezone_field import TimeZoneField
from phone_field import PhoneField
#
#
#
#
#
#
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserModelManager(BaseUserManager):
	"""Model manager for UserModel
	"""
	use_in_migrations = True

	def create_user(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User must have a password")
		if not first_name:
			raise ValueError("User must have a first name")
		if not last_name:
			raise ValueError("User must have a last name")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name,
		)
		user.set_password(password)  # change password to hash
		user.is_admin = False
		user.is_staff = False
		user.save(using=self._db)
		return user

	def create_superuser(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User must have a password")
		if not first_name:
			raise ValueError("User must have a first name")
		if not last_name:
			raise ValueError("User must have a last name")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name
		)

		user.set_password(password)  # change password to hash
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user

	def create_staffuser(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError("User must have an email")
		if not password:
			raise ValueError("User must have a password")
		if not first_name:
			raise ValueError("User must have a first name")
		if not last_name:
			raise ValueError("User must have a last name")

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
			last_name=last_name,
		)
		user.set_password(password)  # change password to hash
		user.is_admin = False
		user.is_staff = True
		user.save(using=self._db)
		return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
	class Meta:
		ordering = [
			'last_name',
			'first_name',
			'middle_name',
			'email'
		]

	GENDER_CHOICES = [
		('M', 'Male'),
		('F', 'Female'),
		('', 'Not Set'),
	]
	email = models.EmailField('email', null=False, blank=False, max_length=64,
		unique=True, db_index=True)
	first_name = models.CharField('first_name', null=False, blank=False, max_length=50)
	last_name = models.CharField('last_name', null=False, blank=False, max_length=50)

	middle_name = models.CharField('middle_name', null=False, blank=True, max_length=50)
	bio = models.CharField('bio', null=False, blank=True, max_length=500, default="")
	phone = PhoneField(blank=True, help_text='Contact phone number')
	email_confirmed = models.BooleanField('email_confirmed', default=False)
	phone_confirmed = models.BooleanField('phone_confirmed', default=False)
	dob = models.DateField('dob', null=True, blank=True)
	gender = models.CharField('gender', max_length=1, choices=GENDER_CHOICES, null=False,
	blank=True, default='')
	timezone = TimeZoneField('timezone', default='Europe/Moscow')
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_admin = models.BooleanField(default=False)
	two_factor_auth = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	client_rating = models.CharField(default='', max_length=15, null=False, blank=True)
	is_banned = models.BooleanField(default=False)
	additional_info = models.CharField(max_length=1024, null=False, blank=True)
	last_password_update = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	tos_version = models.CharField(max_length=20, null=True, blank=False, default='1.0')

	EMAIL_FIELD = 'email'
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name']

	objects = UserModelManager()

	@property
	def full_name(self) -> str:
		"""Constructs user's full name.
		"""
		name = f'{self.last_name} {self.first_name}'
		if self.middle_name:
			name += ' ' + self.middle_name
		return name

	@property
	def short_name(self) -> str:
		"""Constructs user's short name (without patronymic).
		"""
		return f'{self.last_name} {self.first_name}'

	def has_module_perms(self, app_label):
		return self.is_admin

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def __str__(self):
		return "{}".format(self.email)


def path_and_rename(instance, filename):
	path = ''
	ext = filename.split('.')[-1]
	# get filename
	if instance.pk:
		filename = '{}.{}'.format(instance.pk, ext)
	else:
		# set filename as random string
		filename = '{}.{}'.format(uuid4().hex, ext)
	# return the whole path to the file
	return os.path.join(path, filename)


class MetaBannedInfo(models.Model):
	banned_user = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE
	)
	reason = models.CharField(max_length=500, null=False, blank=True)
	employee_id = models.IntegerField(null=False, blank=False)
	expiration = models.DateTimeField(blank=True, null=True)

	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


class ClientPlan(models.Model):
	code = models.CharField(max_length=255, primary_key=True)
	description = models.CharField(max_length=500, null=False, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


class PlannedClient(models.Model):
	plan = models.ForeignKey(
		ClientPlan, to_field='code', on_delete=models.CASCADE)
	client = models.ForeignKey(
		settings.AUTH_USER_MODEL, related_name='user_plans', on_delete=models.CASCADE
	)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


class KYCOperation(models.Model):
	KYC_CHOICES = [
		("OK", 'OK'),
		("PENDING", 'Pending'),
		("BAD", 'Bad'),
	]
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='kyc_info', on_delete=models.CASCADE)
	kys_status = models.CharField(
		'kyc_status', max_length=10, choices=KYC_CHOICES, null=False, blank=True, default='')
	kyc_last_performed = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


class UserImage(models.Model):
	class Meta:
		app_label = 'userAccount'

	account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='account_images',
	                            on_delete=models.CASCADE)
	image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
	is_deleted = models.BooleanField(default=False)
	uploaded_at = models.DateTimeField(auto_now_add=True)


class PhoneType(models.Model):
	class Meta:
		app_label = 'userAccount'

	phone_type = models.CharField(max_length=20, primary_key=True)
	description = models.CharField(max_length=300, null=True, blank=True)

	def __str__(self):
		return self.phone_type


class Phone(models.Model):
	class Meta:
		app_label = 'userAccount'

	account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='account_phones',
	                            on_delete=models.CASCADE)
	phone_number = models.CharField(max_length=13, null=False, blank=False)
	phone_type = models.ForeignKey(PhoneType, on_delete=models.RESTRICT)
	is_deleted = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


class DocumentType(models.Model):
	class Meta:
		app_label = 'userAccount'

	doc_type = models.CharField(max_length=40, primary_key=True)
	description = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return self.doc_type


class AddressType(models.Model):
	class Meta:
		app_label = 'userAccount'

	addr_type = models.CharField(max_length=40, primary_key=True)
	description = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return self.addr_type


class Document(models.Model):
	account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='documents', on_delete=models.CASCADE)
	doc_type = models.ForeignKey(DocumentType, to_field='doc_type', on_delete=models.CASCADE)
	doc_serial = models.PositiveIntegerField(null=True, blank=True, unique=True)
	doc_number = models.PositiveIntegerField(null=True, blank=True, unique=True)
	doc_issued_at = models.DateField(null=True, blank=True)
	doc_issued_by = models.CharField(max_length=100, blank=True, null=True)
	doc_is_confirmed = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)


class BillingAddress(models.Model):
	class Meta:
		app_label = 'userAccount'

	account = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='billing_addresses', on_delete=models.CASCADE)
	addr_type = models.ForeignKey(AddressType, on_delete=models.RESTRICT)
	addr_country = models.CharField(max_length=100, blank=True, null=True)
	addr_city = models.CharField(max_length=100, blank=True, null=True)
	addr_street_1 = models.CharField(max_length=100, blank=True, null=True)
	addr_street_2 = models.CharField(max_length=100, blank=True, null=True)
	addr_building = models.CharField(max_length=20, blank=True, null=True)
	addr_floor = models.CharField(max_length=20, blank=True, null=True)
	addr_number = models.CharField(max_length=30, blank=True, null=True)
	zip_code = models.CharField(max_length=10, blank=True)
	addr_is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
	updated_at = models.DateTimeField(auto_now_add=True, blank=True, null=False)
