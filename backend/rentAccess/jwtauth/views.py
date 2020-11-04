from django.contrib.auth import get_user_model
from rest_framework import response, decorators, permissions, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import UserCreateSerializer, UserLoginSerializer
from userAccount.models import Profile

# TODO: create new accounts when user registers
# TODO: add user and role to response


User = get_user_model()


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def registration(request):
	serializer = UserCreateSerializer(data=request.data)
	permission_classes = (AllowAny,)
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
	permission_classes = (AllowAny,)
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
