from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render
from rest_framework import response, decorators, permissions, status, generics, mixins, exceptions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.viewsets import ViewSet, GenericViewSet

from .permissions import CanRemovePropertyFromGroup, CanDeleteGroup, CanUpdateGroupInfo, IsMemberOfGroup
from .serializers import GroupCreateSerializer, UserGroupMemberCreateSerializer, GroupListSerializer, \
	UserGroupMemberListSerializer, PropertyGroupMemberListSerializer, PropertyGroupMemberCreateSerializer, \
	GroupRetrieveSerializer
from properties.models import Property
from properties.serializers import PropertyListSerializer
from .models import PropertyGroup, UserGroupMembership, PropertyGroupMembership


# Create your views here.


class GroupListCreateView(generics.ListCreateAPIView):
	parser_classes = [JSONParser]

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
	parser_classes = [JSONParser]

	def get_queryset(self, *args, **kwargs):
		queryset = PropertyGroup.objects.prefetch_related(
			"property_groups", "property_groups__user"
		).all()
		return queryset

	def get_permissions(self):
		permission_classes = [IsMemberOfGroup]
		return [permission() for permission in permission_classes]

	def get_serializer_class(self):
		if self.request.method == 'GET':
			return GroupRetrieveSerializer
		return GroupCreateSerializer


class UserMembersListCreateView(generics.ListCreateAPIView):
	parser_classes = [JSONParser]

	def get(self, request, *args, **kwargs):
		if not UserGroupMembership.objects.filter(
				group_id=self.kwargs["pk"],
				user_id=self.request.user.id,
				can_manage_members=True
		).exists():
			raise exceptions.PermissionDenied
		super(UserMembersListCreateView, self).get(self, request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		if not UserGroupMembership.objects.filter(
				group_id=self.kwargs["pk"],
				user_id=self.request.user.id,
				can_add_members=True
		).exists():
			raise exceptions.PermissionDenied
		super(UserMembersListCreateView, self).post(self, request, *args, **kwargs)

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

	def get(self, request, *args, **kwargs):
		if not UserGroupMembership.objects.filter(
				group_id=self.kwargs["pk"],
				user_id=self.request.user.id
		).exists():
			raise exceptions.PermissionDenied
		super(PropertyGroupMemberListCreateView, self).get(self, request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		if not UserGroupMembership.objects.filter(
				group_id=self.kwargs["pk"],
				user_id=self.request.user.id,
				can_add_properties=True
		).exists():
			raise exceptions.PermissionDenied
		super(PropertyGroupMemberListCreateView, self).post(self, request, *args, **kwargs)

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


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.IsAuthenticated])
def bulk_delete_members(request, pk=None):
	"""
	This method implements user login action.
	Version: 1.0

	:param request: incoming POST request
	:return: JSON object with data
	"""
	User = get_user_model()
	try:
		group = PropertyGroup.objects.get(pk=pk)
	except PropertyGroup.DoesNotExist:
		raise Http404
	try:
		owner = group.property_groups.get(user_id=request.user.id)
	except Exception as e:
		raise exceptions.PermissionDenied
	if owner.is_creator or owner.can_remove_members:
		members = request.data.get('members', None)
		if not members:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		members_existing = User.objects.all().filter(id__in=members)
		if not members_existing or len(members_existing) != len(members):
			# here we check whether the properties with given ids exist
			return Response(data={
				'errors'     : [
					"Users with given ids do not exist."
				],
				'status_code': 400
			},
				status=status.HTTP_400_BAD_REQUEST)
		members_in_group = UserGroupMembership.objects.all().filter(
			user_id__in=members,
			group_id=pk)

		if len(members_in_group) != len(members):
			# here we check if properties are already in the group
			return Response(data={
				'errors'     : [
					"Users are not in the group."
				],
				'status_code': 400
			},
				status=status.HTTP_400_BAD_REQUEST)
		if members:
			UserGroupMembership.objects.filter(
				group_id=pk, user_id__in=members
			).delete()
			return response.Response(status=status.HTTP_204_NO_CONTENT)
	else:
		raise exceptions.PermissionDenied


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.IsAuthenticated])
def bulk_delete_properties(request, pk=None):
	"""
	This method implements user login action.
	Version: 1.0

	:param request: incoming POST request
	:return: JSON object with data
	"""
	try:
		group = PropertyGroup.objects.get(pk=pk)
	except PropertyGroup.DoesNotExist:
		raise Http404
	try:
		owner = group.property_groups.get(user_id=request.user.id)
	except Exception as e:
		raise exceptions.PermissionDenied
	if owner.is_creator or owner.can_delete_properties:
		properties_input = request.data.get('properties', None)

		if not properties_input:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		properties_existing = Property.objects.all().prefetch_related(
			"owners",
			"owners__user"
		).filter(id__in=properties_input)
		if not properties_existing or len(properties_input) != len(properties_existing):
			# here we check whether the properties with given ids exist
			return Response(data={
				'errors'     : [
					"Properties with given ids do not exist."
				],
				'status_code': 400
			},
				status=status.HTTP_400_BAD_REQUEST)
		properties_in_group = PropertyGroupMembership.objects.all().filter(
			premises_id__in=properties_input,
			group_id=pk)

		if len(properties_in_group) != len(properties_input):
			# here we check if properties are already in the group
			return Response(data={
				'errors'     : [
					"Properties are not in the group."
				],
				'status_code': 400
			},
				status=status.HTTP_400_BAD_REQUEST)
		if properties_input:
			PropertyGroupMembership.objects.filter(
				group_id=pk, premises_id__in=properties_input
			).delete()
			return response.Response(status=status.HTTP_204_NO_CONTENT)
	else:
		raise exceptions.PermissionDenied
# permission_classes = (AllowAny,)
