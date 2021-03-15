from django.http import Http404
from django.shortcuts import render
from rest_framework import response, decorators, permissions, status, generics
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.db.models import Q
from .serializers import GroupCreateSerializer, UserGroupMemberCreateSerializer, GroupListSerializer, \
	UserGroupMemberListSerializer, PropertyGroupMemberListSerializer, PropertyGroupMemberCreateSerializer
from properties.models import Property
from properties.serializers import PropertyListSerializer
from .models import PropertyGroup, UserGroupMembership, PropertyGroupMembership


# Create your views here.


class GroupListCreateView(generics.ListCreateAPIView):

	# send_booking_email_to_client(has_key=False, data=data, duration=0)

	def get_queryset(self, *args, **kwargs):

		queryset = PropertyGroup.objects.prefetch_related(
			"property_groups", "property_groups__user"
		).all().filter(
			Q(property_groups__user=self.request.user)
		)
		return queryset

	def get_serializer_class(self):
		if self.request.method == "GET":
			return GroupListSerializer
		return GroupCreateSerializer


class GroupRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):

	def get_queryset(self, *args, **kwargs):

		queryset = PropertyGroup.objects.prefetch_related(
			"property_groups", "property_groups__user"
		).all().filter(
			Q(property_groups__user=self.request.user)
		)
		return queryset

	def get_serializer_class(self):
		return GroupCreateSerializer


class UserMembersListCreateView(generics.ListCreateAPIView):
	def get_queryset(self, *args, **kwargs):
		queryset = UserGroupMembership.objects.prefetch_related(
			"group"
		).select_related("user").all().filter(
			Q(group_id=self.kwargs["pk"])
		)

		return queryset

	def get_serializer_context(self):
		context = super(UserMembersListCreateView, self).get_serializer_context()
		context.update({
			"group_id": self.kwargs["pk"]
			# extra data
		})
		return context

	def get_serializer_class(self):
		if self.request.method == "GET":
			return UserGroupMemberListSerializer
		return UserGroupMemberCreateSerializer


class PropertyGroupMemberListCreateView(generics.ListCreateAPIView):
	parser_classes = [JSONParser]

	def get_queryset(self, *args, **kwargs):
		queryset = Property.objects.all().select_related(
			'availability', 'property_address', 'property_address__city', 'property_type')
		queryset = queryset.filter(
			Q(mem_groups__group_id=self.kwargs["pk"])
		).prefetch_related('property_images')
		return queryset

	def get_serializer_context(self):
		context = super(PropertyGroupMemberListCreateView, self).get_serializer_context()
		context.update({
			"group_id": self.kwargs["pk"]
			# extra data
		})
		return context

	def get_serializer(self, *args, **kwargs):
		if isinstance(kwargs.get("data", {}), list):
			kwargs["many"] = True

		return super(PropertyGroupMemberListCreateView, self).get_serializer(*args, **kwargs)

	def create(self, request, *args, **kwargs):
		context = self.get_serializer_context()
		write_serializer = PropertyGroupMemberCreateSerializer(
			data=request.data,
			context=context
		)
		write_serializer.is_valid(raise_exception=True)
		instance = self.perform_create(write_serializer)
		queryset = Property.objects.all().select_related(
			'availability', 'property_address', 'property_address__city', 'property_type')
		queryset = queryset.filter(
			Q(mem_groups__group_id=self.kwargs["pk"])
		).prefetch_related('property_images')
		read_serializer = PropertyListSerializer(queryset, many=True)

		headers = self.get_success_headers(read_serializer.data)
		return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def get_serializer_class(self):
		if self.request.method == "GET":
			return PropertyListSerializer
		return PropertyGroupMemberCreateSerializer
