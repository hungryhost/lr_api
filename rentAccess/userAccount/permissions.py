from django.contrib.auth.models import User
from rest_framework import permissions


# TODO: Update permissions depending on roles
#
from .models import Profile, UserImages, Documents


class PersonalInfoAccessList(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		return obj.account == request.user or request.user.is_superuser

class IsOwnerOrSuperuser(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		return obj.user == request.user or request.user.is_superuser


class IsCurrentUserOrSuperuser(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		return obj == request.user or request.user.is_superuser
