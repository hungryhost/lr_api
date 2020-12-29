import rest_framework_simplejwt
from django.http import Http404
from rest_framework import status, exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
	# Call REST framework's default exception handler first,
	# to get the standard error response.
	response = exception_handler(exc, context)
	if isinstance(exc, Http404):
		response.data = {}
		errors = ["Not Found : Resource does not exist"]
		response.data['errors'] = errors
		response.data['status_code'] = 404
		return response

	if isinstance(exc, rest_framework_simplejwt.exceptions.InvalidToken):
		response.data = {}
		errors = ["Invalid Token : Given token is not valid"]
		response.data['errors'] = errors
		response.data['status_code'] = 401
		return response
	if isinstance(exc, exceptions.NotAuthenticated):
		response.data = {}
		errors = ["Unauthorized : Authentication not provided."]
		response.data['errors'] = errors
		response.data['status_code'] = 401
		return response
	if isinstance(exc, exceptions.PermissionDenied):
		response.data = {}
		errors = 'Forbidden : You do not have necessary permissions'
		response.data['errors'] = errors
		response.data['status_code'] = 403
	"""
	if response is not None:
		# check if exception has dict items
		if hasattr(exc.detail, 'items'):
			# remove the initial value
			response.data = {}
			errors = []
			for key, value in exc.detail.items():
				# append errors into the list
				errors.append("{} : {}".format(key, "".join(value)))

			# add property errors to the response
			response.data['errors'] = errors

		# serve status code in the response
		response.data['status_code'] = response.status_code
	"""
	return response
