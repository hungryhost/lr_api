from django.contrib.auth.models import User
from django.db import models
from cities_light.models import City
# this file contains common models for the whole project
# additional models may be added and should be documented


class ActionType(models.Model):
	"""
	This model describes types of actions that can be performed.
	Used for logs only.
	WARNING: MUST BE FILLED OUT INITIALLY
	"""
	class Meta:
		db_table = 'action_types'
	act_type = models.CharField(max_length=30, primary_key=True)
	description = models.CharField(max_length=150)


class ResultType(models.Model):
	"""
	This model describes types of results that can happen after a
	certain request or action. Used for logs only.
	WARNING: MUST BE FILLED OUT INITIALLY
	"""
	class Meta:
		db_table = 'action_result_types'
	res_type = models.CharField(max_length=30, primary_key=True)
	description = models.CharField(max_length=150)


class SupportedCity(models.Model):
	class Meta:
		db_table = 'supported_cities'

	name = models.CharField(max_length=255, blank=True, null=False, primary_key=True)
	city = models.ForeignKey(City, related_name='supported_cities',
		on_delete=models.CASCADE, null=False, blank=False)
