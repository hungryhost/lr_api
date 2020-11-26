from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.
from userAccount.models import *


class Property(models.Model):
	author = models.ForeignKey(Profile, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	body = models.TextField()
	price = models.PositiveIntegerField()
	active = models.BooleanField(default=True)
	# TODO: add multiple images that would be available with details view

	def __str__(self):
		return self.title


class Ownership(models.Model):
	premises = models.ForeignKey(Property, on_delete=models.CASCADE)
	owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
	is_initial_owner = models.BooleanField(default=False)


class PropertyLog(models.Model):
	listed_prop = models.ForeignKey(Property, on_delete=models.CASCADE)
	# lock_id =
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	CHOICES = [
		('POST', 'Post Request'),
		('PUT', 'PUT Request'),
		('PATCH', 'PATCH Request'),
		('DELETE', 'DELETE Request'),
		('DEACTIVATE', 'DEACTIVATE property'),
		('GIVE_ACC', 'Give access to property'),
	]
	action = models.CharField(max_length=300, choices=CHOICES)
	act_time = models.DateTimeField('act_time', null=False, auto_now_add=True)
	result = models.BooleanField('result', null=False)


class PremisesImages(models.Model):
	premises = models.ForeignKey(Property, on_delete=models.CASCADE)
	filepath = models.CharField(max_length=200, null=False, blank=False)
	uploaded_at = models.DateTimeField(auto_now_add=True)
	is_deleted = models.BooleanField(default=False)
	is_main = models.BooleanField(default=False)


class PremisesAddresses(models.Model):
	premises = models.ForeignKey(Property, on_delete=models.CASCADE)
	paddr_country = models.CharField(max_length=100, blank=True, null=True)
	paddr_city = models.CharField(max_length=100, blank=True, null=True)
	paddr_street_1 = models.CharField(max_length=100, blank=True, null=True)
	paddr_street_2 = models.CharField(max_length=100, blank=True, null=True)
	paddr_building = models.CharField(max_length=20, blank=True, null=True)
	paddr_floor = models.CharField(max_length=20, blank=True, null=True)
	paddr_number = models.CharField(max_length=30, blank=True, null=True)
	pzip_code = models.CharField(max_length=10, blank=True)
