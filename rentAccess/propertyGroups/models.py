from django.db import models
from properties.models import Property
# Create your models here.
from django.conf import settings


class PropertyGroup(models.Model):
	title = models.CharField(max_length=255, null=False, blank=False)
	description = models.TextField(max_length=500, null=False, blank=False)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

	def __str__(self):
		return self.title


class PropertyGroupMembership(models.Model):
	premises = models.ForeignKey(
		Property,
		related_name='mem_groups',
		on_delete=models.CASCADE,
		null=False,
		blank=False
	)
	group = models.ForeignKey(
		PropertyGroup,
		related_name='mem_property_groups',
		on_delete=models.CASCADE,
		null=False,
		blank=False
	)
	added_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='added_properties',
		on_delete=models.SET_NULL, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

	def __str__(self):
		return self.premises.title + " in " + self.group.title


class UserGroupMembership(models.Model):

	class Meta:
		unique_together = [['user', 'group']]

	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_groups',
		on_delete=models.SET_NULL, null=True, blank=False)
	group = models.ForeignKey(PropertyGroup, related_name='property_groups', on_delete=models.CASCADE, null=False, blank=False)
	is_creator = models.BooleanField(default=False, null=False)

	can_add_properties = models.BooleanField(default=False, null=False)
	can_delete_properties = models.BooleanField(default=False, null=False)

	can_book_properties = models.BooleanField(default=True, null=False)

	recursive_ownership = models.BooleanField(default=False, null=False)

	can_add_members = models.BooleanField(default=False, null=False)
	can_remove_members = models.BooleanField(default=False, null=False)
	can_manage_members = models.BooleanField(default=False, null=False)
	can_update_info = models.BooleanField(default=False, null=False)
	can_delete_group = models.BooleanField(default=False, null=False)
	joined_with_code = models.BooleanField(default=False, null=False)
	joined_with_link = models.BooleanField(default=False, null=False)

	added_by_user_id = models.IntegerField(null=True, blank=True)
	added_by_owner_id = models.IntegerField(null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
	updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)

	def __str__(self):
		return self.user.full_name + " is a member of " + self.group.title