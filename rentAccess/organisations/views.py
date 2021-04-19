from django.http import Http404
from django.shortcuts import render
from rest_framework import response, decorators, permissions, status, generics
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.db.models import Q
from .serializers import OrganisationCreateSerializer, OrganisationListSerializer, \
	OrganisationMemberSerializer, UserOrganisationMemberCreateSerializer, PropertyOrganisationMemberCreateSerializer, \
	OrganisationPropertyList
from properties.models import Property
from properties.serializers import PropertyListSerializer
from .models import Organisation, OrganisationMember, OrganisationProperty


# Create your views here.


class OrganisationsListCreate(generics.ListCreateAPIView):

	def get_queryset(self, *args, **kwargs):

		queryset = Organisation.objects.prefetch_related(
			"member_tied_org",
		).all().filter(
			Q(member_tied_org__user=self.request.user)
		)
		return queryset

	def get_serializer_class(self):
		if self.request.method == "GET":
			return OrganisationListSerializer
		return OrganisationCreateSerializer


class OrganisationRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
	http_method_names = ['get', 'delete', 'put']

	def get_queryset(self, *args, **kwargs):
		queryset = Organisation.objects.prefetch_related(
			"member_tied_org",
		).all().filter(
			Q(member_tied_org__user=self.request.user)
		)
		return queryset

	def get_serializer_class(self):
		return OrganisationCreateSerializer


class UserOrganisationMembersListCreateView(generics.ListCreateAPIView):
	def get_queryset(self, *args, **kwargs):
		queryset = OrganisationMember.objects.prefetch_related(
			"organisation"
		).select_related("user").all().filter(
			Q(organisation_id=self.kwargs["pk"])
		)
		return queryset

	def get_serializer_context(self):
		context = super(UserOrganisationMembersListCreateView, self).get_serializer_context()
		context.update({
			"organisation_id": self.kwargs["pk"]
			# extra data
		})
		return context

	def get_serializer_class(self):
		if self.request.method == "GET":
			return OrganisationMemberSerializer
		return UserOrganisationMemberCreateSerializer


class PropertyOrganisationMemberListCreateView(generics.ListCreateAPIView):
	parser_classes = [JSONParser]

	def get_queryset(self, *args, **kwargs):
		queryset = OrganisationProperty.objects.all().select_related(
			'premises', 'premises__availability', 'premises__property_address',
			'premises__property_type').prefetch_related('premises__property_images')
		queryset = queryset.filter(
			id=self.kwargs["pk"])
		return queryset

	def get_serializer_context(self):
		context = super(PropertyOrganisationMemberListCreateView, self).get_serializer_context()
		context.update({
			"organisation_id": self.kwargs["pk"]
			# extra data
		})
		return context

	def get_serializer(self, *args, **kwargs):
		if isinstance(kwargs.get("data", {}), list):
			kwargs["many"] = True

		return super(PropertyOrganisationMemberListCreateView, self).get_serializer(*args, **kwargs)

	def create(self, request, *args, **kwargs):
		context = self.get_serializer_context()
		write_serializer = PropertyOrganisationMemberCreateSerializer(
			data=request.data,
			context=context
		)
		write_serializer.is_valid(raise_exception=True)
		instance = self.perform_create(write_serializer)
		read_serializer = OrganisationPropertyList(instance, many=True)
		headers = self.get_success_headers(read_serializer.data)
		return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def get_serializer_class(self):
		if self.request.method == "GET":
			return OrganisationPropertyList
		return PropertyOrganisationMemberCreateSerializer
