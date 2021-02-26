from django.db import models
from properties.models import Property
# Create your models here.
from django.conf import settings


class PropertyGroup(models.Model):
	title = models.CharField(max_length=50, null=False, blank=False)
	description = models.TextField(max_length=500, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)


class PropertyGroupMembership(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='p_groups',
		on_delete=models.CASCADE, null=False, blank=False)
	premises = models.ForeignKey(Property, related_name='groups', on_delete=models.CASCADE, null=False, blank=False)