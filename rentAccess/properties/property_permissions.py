from django.contrib.auth.models import User
from rest_framework import permissions


class PropertyOwner100(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.owners.filter(user=request.user).exists() and \
				obj.owners.get(user=request.user).permission_level_id == 100:
			return True
		return False


class PropertyOwner200(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.owners.filter(user=request.user).exists() and \
				obj.owners.get(user=request.user).permission_level_id == 200:
			return True
		return False


class PropertyOwner300(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.owners.filter(user=request.user).exists() and \
				obj.owners.get(user=request.user).permission_level_id == 300:
			return True
		return False


class PropertyOwner400(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj.owners.filter(user=request.user).exists() and \
				obj.owners.get(user=request.user).permission_level_id == 400:
			return True
		return False


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