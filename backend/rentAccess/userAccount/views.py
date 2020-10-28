from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from .models import Profile
from .serializers import ProfileSerializer

# TODO: add separate classes for POST, GET, PUT, PATCH


class ProfileList(generics.ListAPIView):
	permission_classes = (permissions.IsAdminUser, )
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer


class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset = Profile.objects.all()
	serializer_class = ProfileSerializer
