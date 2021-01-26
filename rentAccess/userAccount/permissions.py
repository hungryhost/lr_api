from django.contrib.auth.models import User
from rest_framework import permissions


# TODO: Update permissions depending on roles
#

class IsOwnerOrSuperuser(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		return obj.user == request.user or request.user.is_superuser

