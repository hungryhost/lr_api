from rest_framework import permissions


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


class CanUpdateBooking(permissions.BasePermission):
	r"""
	obj: booking object
	"""
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		try:
			owner = obj.booked_property.owners.get(user=request.user)
		except Exception as e:
			owner = None
		if owner:
			if owner.can_manage_bookings:
				return True
		else:
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


class CanRetrieve(permissions.BasePermission):
	def has_permission(self, request, view):
		return request.user and request.user.is_authenticated

	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser or \
				obj.booked_property.owners.filter(user=request.user).exists() or \
				obj.client_email == request.user.email:
			return True
		return False