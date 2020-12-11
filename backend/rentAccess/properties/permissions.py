from django.contrib.auth.models import User
from rest_framework import permissions

from .models import Ownership


class IsOwnerOrSuperuser(permissions.BasePermission):
	"""
	Permissions class for properties.
	Author: Y. Borodin (gitlab: yuiborodin)
	Version: 1.0
	Last Update: 16.11.2020
	"""
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		return obj.author == request.user or request.user.is_superuser


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
