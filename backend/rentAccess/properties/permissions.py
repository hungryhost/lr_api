from django.contrib.auth.models import User
from rest_framework import permissions

from .models import Ownership, Bookings

r"""
	Provides a set of permissions for the properties
		- /properties/ : GET/POST : isAuthenticated
		- /properties/<properties:id>/owners/
			- GET: isOwner [with all permission levels]
			- POST, GET[Retrieve], PATCH, DELETE: isOwner [with permission level 300 or 400]
		- /properties/<properties:id>/bookings/ : only owners
"""


class IsOwnerOrSuperuser(permissions.BasePermission):
	"""
	Permissions class for properties.
	"""
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.owners.filter(user=request.user).exists() or obj.visibility == 100 or request.user.is_superuser:
			return True
		return False


class BookingIsAdminOfPropertyOrSuperuser(permissions.BasePermission):
	# This permission class is used for editing a booking

	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if obj.booked_property.owners.filter(user=request.user).exists() or request.user.is_superuser:
			return True
		return False


class IsClientUser(permissions.BasePermission):
	# TODO: complete this permission class in order to use for clients
	pass


class IsInitialOwner(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		ownership_status = Ownership.objects.filter(owner=request.user,
													premises=obj.premises).exists()
		return ownership_status
