from django.contrib.auth.models import User
from rest_framework import permissions
from .models import Ownership


class IsPublicProperty(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.visibility == 100:
			return True
		return False


class CanBeRetrieved(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.visibility == 100 or (obj.owners.filter(user=request.user).exists() or request.user.is_superuser):
			return True
		return False


class CanUpdateInfo(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_edit or request.user.is_superuser:
			return True
		return False


class CanDeleteProperty(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_delete or request.user.is_superuser:
			return True
		return False


class CanAddImages(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_add_images or request.user.is_superuser:
			return True
		return False


class CanDeleteImages(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_delete_images or request.user.is_superuser:
			return True
		return False


class CanAddOwners(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.can_add_owners or request.user.is_superuser:
			return True
		return False


class CanManageOwners(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.can_manage_owners or request.user.is_superuser:
			return True
		return False


class CanDeleteOwners(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.can_delete_owners or request.user.is_superuser:
			return True
		return False


class CanAddLocks(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_add_locks or request.user.is_superuser:
			return True
		return False


class CanManageLocks(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_manage_locks or request.user.is_superuser:
			return True
		return False


class CanDeleteLocks(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_delete_locks or request.user.is_superuser:
			return True
		return False


class CanAddToGroup(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_add_to_group or request.user.is_superuser:
			return True
		return False


class CanAddToOrganisation(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.owners.get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		if owner.can_add_to_organisation or request.user.is_superuser:
			return True
		return False


class InOwnership(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			obj.premises.owners.all().get(user=request.user)
		except Ownership.DoesNotExist:
			return False
		return True
