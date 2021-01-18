from django.contrib.auth.models import User
from rest_framework import permissions

from .models import Ownership, Bookings


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


class IsClientOfBooking(permissions.BasePermission):
	r"""
	obj: booking object
	"""
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.client_email == request.user.email or request.user.is_superuser:
			return True
		return False


class IsOwnerLevel100(permissions.BasePermission):
	r"""
	obj: booking object
	"""
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if (obj.booked_property.owners.filter(user=request.user).exists()
	and obj.booked_property.owners.get(user=request.user).permission_level_id == 100
		) or request.user.is_superuser:
			return True
		return False


class IsOwnerLevel200(permissions.BasePermission):
	r"""
	obj: booking object
	"""

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if (obj.booked_property.owners.filter(user=request.user).exists()
	and obj.booked_property.owners.get(user=request.user).permission_level_id == 200
		) or request.user.is_superuser:
			return True
		return False


class IsOwnerLevel300(permissions.BasePermission):
	r"""
	obj: booking object
	"""

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if (obj.booked_property.owners.filter(user=request.user).exists()
	and obj.booked_property.owners.get(user=request.user).permission_level_id == 300
		) or request.user.is_superuser:
			return True
		return False


class IsOwnerLevel400(permissions.BasePermission):
	r"""
	obj: booking object
	"""

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if (obj.booked_property.owners.filter(user=request.user).exists()
	and obj.booked_property.owners.get(user=request.user).permission_level_id == 400
		) or request.user.is_superuser:
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


class IsInitialOwner(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		ownership_status = Ownership.objects.filter(owner=request.user,
													premises=obj.premises).exists()
		return ownership_status
