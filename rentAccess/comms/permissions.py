from django.contrib.auth.models import User
from rest_framework import permissions


class IsOwnerOfRequest(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser or obj.email == request.user.email:
			return True
		return False
