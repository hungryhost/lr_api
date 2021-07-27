from django.contrib.auth.models import User
from rest_framework import permissions


# TODO: Update permissions depending on roles
#

class CanAddPropertyToGroup(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		return obj == request.user or request.user.is_superuser


class CanRemovePropertyFromGroup(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.property_groups.get(user_id=request.user.id)
		except Exception as e:
			return False
		if owner.is_creator or owner.can_delete_properties:
			return True


class CanDeleteGroup(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.property_groups.get(user_id=request.user.id)
		except Exception as e:
			return False
		if owner.is_creator or owner.can_delete_group or request.user.is_superuser:
			return True
		return False


class CanUpdateGroupInfo(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.property_groups.get(user_id=request.user.id)
		except Exception as e:
			return False
		if owner.is_creator or owner.can_update_info or request.user.is_superuser:
			return True
		return False


class IsMemberOfGroup(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.property_groups.get(user_id=request.user.id)
		except Exception as e:
			return False
		if request.method == 'GET':
			return True
		if request.method in ['PUT', 'PATCH']:
			if owner.can_update_info or owner.is_creator or request.user.is_superuser:
				return True
		if request.method == 'DELETE':
			if owner.can_delete_group or owner.is_creator or request.user.is_superuser:
				return True
		return False
