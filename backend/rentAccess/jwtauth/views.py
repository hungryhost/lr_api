from django.contrib.auth import get_user_model
from rest_framework import response, decorators, permissions, status
# from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .serializers import UserCreateSerializer, UserLoginSerializer
from userAccount.models import Profile

# TODO: create blacklist for tokens


User = get_user_model()


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
	serializer = UserCreateSerializer(data=request.data)
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
			"account_id": profile.id,
			"username": str(user.email),
			"first_name": str(user.first_name),
			"last_name": str(user.last_name),
			"account_type": str(profile.account_type),
		},
	}
	return response.Response(res, status.HTTP_201_CREATED)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def login(request):
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
			"account_id": profile.id,
			"username": str(user.email),
			"first_name": str(user.first_name),
			"last_name": str(user.last_name),
			"account_type": str(profile.account_type),
		},
	}
	return response.Response(res, status.HTTP_200_OK)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.IsAuthenticated])
def logout(request):
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
	tokens = OutstandingToken.objects.filter(user_id=request.user.id)
	for token in tokens:
		t, _ = BlacklistedToken.objects.get_or_create(token=token)

	return Response(status=status.HTTP_205_RESET_CONTENT)


