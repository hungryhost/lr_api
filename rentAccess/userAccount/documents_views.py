from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from .models import Document
from .permissions import IsOwnerOrSuperuser
from .documents_serializers import DocumentsSerializer


class ProfileDocumentsViewSet(viewsets.ViewSet, mixins.ListModelMixin, viewsets.GenericViewSet):

	def get_queryset(self):
		return Document.objects.all()

	def list(self, request, *args, **kwargs):
		queryset = Document.objects.all().filter(account=self.request.user)
		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = DocumentsSerializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = DocumentsSerializer(queryset, many=True)
		return Response(serializer.data)

	def create(self, request):
		serializer = DocumentsSerializer(
			data=self.request.data,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	def partial_update(self, request, pk=None):
		instance = get_object_or_404(Document, account=self.request.user, pk=pk)
		serializer = DocumentsSerializer(
			instance,
			data=self.request.data,
			partial=True,
			context={'request': request}
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data, status=status.HTTP_200_OK)

	def get_serializer_class(self):
		return DocumentsSerializer

	def get_object(self):
		return get_object_or_404(Document, account=self.request.user)

	def get_permissions(self):
		permission_classes = [IsOwnerOrSuperuser, ]
		return [permission() for permission in permission_classes]

