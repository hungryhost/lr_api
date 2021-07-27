from django.shortcuts import render
from bookings.models import Booking
from django.db.models import Q, Prefetch
from django.http import Http404
from rest_framework import generics, permissions, status, response, serializers, viewsets, mixins, exceptions, \
	decorators, filters
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import AvailabilityExceptionSerializer
from properties.models import AvailabilityException, Property
from register.models import Key
from rest_framework import generics
# Create your views here.


class AvailabilityExceptionListCreateView(generics.ListCreateAPIView):
	serializer_class = AvailabilityExceptionSerializer

	def create(self, request, *args, **kwargs):
		user = self.request.user

		try:
			related_property = Property.objects.prefetch_related(
				'owners', 'owners__user'
			).get(pk=self.kwargs['pk'])
		except Property.DoesNotExist:
			raise Http404
		permitted_owners = []
		ownerships = [owner for owner in related_property.owners.all()]
		for owner in ownerships:
			if owner.can_edit:
				permitted_owners.append(owner.user)
		if user not in permitted_owners:
			raise exceptions.PermissionDenied
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

	def get(self, request, *args, **kwargs):
		try:
			related_property = Property.objects.prefetch_related(
				'owners', 'owners__user'
			).get(pk=self.kwargs['pk'])
		except Property.DoesNotExist:
			raise Http404
		ownerships = [owner.user for owner in related_property.owners.all()]
		if self.request.user not in ownerships or related_property.visibility != 100:
			raise exceptions.PermissionDenied
		return super(self.__class__, self).get(self, request, *args, **kwargs)

	def get_queryset(self, *args, **kwargs):
		queryset = AvailabilityException.objects.all().filter(
			Q(parent_availability__premises_id=self.kwargs["pk"])
		)

		return queryset

	def get_serializer_context(self):
		context = super(AvailabilityExceptionListCreateView, self).get_serializer_context()
		context.update({
			"premises_id": self.kwargs["pk"]
			# extra data
		})
		return context


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.IsAuthenticated])
def request_password_reset(request):
	"""
	This method implements user logout_all endpoint.
	Version: 1.0

	:param request: incoming POST request
	:return: JSON object with status code
	"""
	pass

	return Response(status=status.HTTP_205_RESET_CONTENT)


class AvailabilityExceptionViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):

	def get_calendar_list(self, request, pk=None):
		obj = self.get_object(property_id=pk)
		serializer = AvailabilityExceptionSerializer(
			obj,
			context={'request': request, 'property_id': pk}
		)
		return Response(serializer.data)

	def get_queryset(self):
		return AvailabilityException.objects.all()

	def get_permissions(self):
		permission_classes = [permissions.IsAuthenticated]
		return [permission() for permission in permission_classes]

	def get_object(self, property_id=None):
		try:
			obj = AvailabilityException.objects.get(
				parent_availability__premises_id=property_id)
			self.check_object_permissions(self.request, obj)
			return obj
		except AvailabilityException.DoesNotExist:
			raise Http404

	def get_serializer_class(self):
		return AvailabilityExceptionSerializer