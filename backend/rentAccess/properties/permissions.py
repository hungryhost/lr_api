from django.contrib.auth.models import User
from rest_framework import permissions


# TODO: Update permissions depending on roles
#


<<<<<<< HEAD
class IsAuthor(permissions.BasePermission):
=======
class IsOwnerOrSuperuser(permissions.BasePermission):
	message = {'Forbidden': ['You do not have necessary permissions']}

>>>>>>> backend-profile
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		return obj.author.id == request.user.id or request.user.is_superuser