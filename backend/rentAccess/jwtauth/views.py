import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import response, decorators, permissions, status
# from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .utils import username_generate_from_email
from .tasks import email_confirmation_task
from .serializers import UserCreateSerializer, UserLoginSerializer
from userAccount.models import Profile
from django.contrib.sites.shortcuts import get_current_site


User = get_user_model()


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
	"""
	This method implements user registration.
	Version 1.0

	:param request: incoming POST request
	:return: JSON object with data
	"""
	serializer = UserCreateSerializer(data=request.data)
	# permission_classes = (AllowAny,)
	if not serializer.is_valid():
		return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
	user = serializer.save()
	curr_user = User.objects.get(username=user.username)
	username = username_generate_from_email(curr_user.email, curr_user.id)
	curr_user.username = username
	curr_user.save()
	profile = Profile.objects.get(user=curr_user)
	refresh = RefreshToken.for_user(user)
	res = {
		"refresh": str(refresh),
		"access": str(refresh.access_token),
		"personal_info": {
			"account_id": profile.user.id,
			"username": str(curr_user.username),
			"email": str(curr_user.email),
			"first_name": str(curr_user.first_name),
			"last_name": str(curr_user.last_name),
			"account_type": str(profile.account_type),
		},
	}
	# TODO: owed refactoring, what's below belongs in another file
	current_site = get_current_site(request).domain
	relative_link = reverse('email_verification')
	absolute_url = 'http://'+current_site+relative_link+'?token='+str(refresh.access_token)
	email_body = (
			"Hi, " + user.first_name +
			"!\nPlease verify your email "+user.email+" with the link below.\n" +
			"<a href="+'"'+absolute_url+'"'+">Confirm</a>")
	data = {
		"subject": "Verify your email at lockandrent.ru",
		"body": email_body,
		"first_name": user.first_name,
		"confirmation_link": absolute_url,
		"email": user.email
	}
	# email_confirmation_task.delay(0, data)
	return response.Response(res, status.HTTP_201_CREATED)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def login(request):
	"""
	This method implements user login action.
	Version: 1.0

	:param request: incoming POST request
	:return: JSON object with data
	"""
	serializer = UserLoginSerializer(data=request.data)
	# permission_classes = (AllowAny,)
	if not serializer.is_valid():
		return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
	user = serializer.save()
	curr_user = User.objects.get(username=user.username)
	profile = Profile.objects.get(user=curr_user)
	refresh = RefreshToken.for_user(user)

	res = {
		"refresh": str(refresh),
		"access": str(refresh.access_token),
		"personal_info": {
			"account_id": profile.user.id,
			"username": str(user.username),
			"email": str(user.email),
			"first_name": str(user.first_name),
			"last_name": str(user.last_name),
			"account_type": str(profile.account_type),
		},
	}
	return response.Response(res, status.HTTP_200_OK)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.IsAuthenticated])
def logout(request):
	"""
	This method implements user logout endpoint.
	Version: 1.0

	:param request: incoming POST request
	:return: JSON object with status code
	"""
	try:
		refresh_token = request.data["refresh"]
		token = RefreshToken(refresh_token)
		token.blacklist()
		return Response(status=status.HTTP_205_RESET_CONTENT)
	except Exception as e:
		return Response(status=status.HTTP_400_BAD_REQUEST)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.IsAuthenticated])
def logout_all(request):
	"""
	This method implements user logout_all endpoint.
	Version: 1.0

	:param request: incoming POST request
	:return: JSON object with status code
	"""
	tokens = OutstandingToken.objects.filter(user_id=request.user.id)
	for token in tokens:
		t, _ = BlacklistedToken.objects.get_or_create(token=token)

	return Response(status=status.HTTP_205_RESET_CONTENT)


@decorators.api_view(["GET"])
@decorators.permission_classes([permissions.AllowAny])
def email_verification(request):
	"""
	This method implements email verification endpoint.

	:param request: incoming GET request.
	"""
	token = request.GET.get('token')
	try:
		payload = jwt.decode(token, settings.SECRET_KEY)
		user = User.objects.get(id=payload['user_id'])
		profile = Profile.objects.get(user=user)
		if not profile.is_confirmed:
			profile.is_confirmed = True
			profile.save()
		return Response({
			'email': 'Email confirmed'
		}, status=status.HTTP_200_OK)
	# TODO: owed refactoring, adjust error handler for these exceptions below
	except jwt.exceptions.ExpiredSignatureError as identifier:
		data = {}
		errors = ["token: Expired token (activation failed)"]
		data['errors'] = errors
		data['status_code'] = 400
		return Response(data, status=status.HTTP_400_BAD_REQUEST)
	except jwt.exceptions.DecodeError as identifier:
		data = {}
		errors = ["token: Invalid token (activation failed)"]
		data['errors'] = errors
		data['status_code'] = 400
		return Response(data, status=status.HTTP_400_BAD_REQUEST)
