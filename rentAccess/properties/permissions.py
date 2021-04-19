from django.contrib.auth.models import User
from rest_framework import permissions

from properties.models import Ownership


class IsSuperUser(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser:
			return True
		return False


class IsOwner(permissions.BasePermission):
	r"""
	object: property
	This permission class checks whether a user is an owner.
	Permission level does not matter.
	"""
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.owners.filter(user=request.user).exists() or request.user.is_superuser:
			return True
		return False


class IsInitialOwner(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		ownership_status = Ownership.objects.filter(owner=request.user,
													premises=obj.premises).exists()
		return ownership_status
