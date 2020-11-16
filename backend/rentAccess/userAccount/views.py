from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrSuperuser
from .models import Profile
from .serializers import ProfileSerializer, ChangePasswordSerializer


# TODO: add separate classes for POST, GET, PUT, PATCH


class ProfileList(generics.ListAPIView):
	permission_classes = (permissions.IsAdminUser, )
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser,)
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer


class ChangePasswordView(generics.UpdateAPIView):
	queryset = User.objects.all()
	permission_classes = (IsAuthenticated, IsOwnerOrSuperuser,)
	serializer_class = ChangePasswordSerializer
