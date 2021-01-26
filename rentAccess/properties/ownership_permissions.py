from rest_framework import permissions


class CanAddOwner(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	# for object level permissions
	def has_object_permission(self, request, view, obj):
		if obj(user=request.user).exists() and \
				obj.owners.get(user=request.user).permission_level_id == 100:
			return True
		return False
