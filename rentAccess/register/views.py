from django.db.models import Prefetch
from django.http import Http404
from rest_framework import generics, status, exceptions

from properties.permissions import IsOwner
from .models import Lock, Card, Key
from locks.serializers import LockSerializer
from properties.models import Property, Ownership
from .serializers import CardSerializer, KeySerializer
from rest_framework.response import Response
from locks.serializers import AddLockToPropertySerializer

# TODO: Add permissions and logs
# TODO: replace this to locks and keys apps


class LockList(generics.ListCreateAPIView):
    queryset = Lock.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddLockToPropertySerializer
        return LockSerializer


class CardList(generics.ListCreateAPIView):
    serializer_class = CardSerializer

    def get(self, request, *args, **kwargs):
        try:
            property_owners = Property.objects.prefetch_related(
                Prefetch('owners', queryset=Ownership.objects.select_related('user').all())).get(pk=self.kwargs['pk'])
        except Property.DoesNotExist:
            raise Http404
        ownerships = [owner.user for owner in property_owners.owners.all()]
        if not (self.request.user in ownerships) and self.request.method == "GET":
            raise exceptions.PermissionDenied
        return super(self.__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        queryset = Card.objects.all()
        lock_id = self.kwargs.get('lock_id', None)
        queryset = queryset.filter(lock_id__tied_lock=lock_id)
        return queryset


class KeyList(generics.ListCreateAPIView):
    serializer_class = KeySerializer

    def get(self, request, *args, **kwargs):
        try:
            property_owners = Property.objects.prefetch_related(
                Prefetch('owners', queryset=Ownership.objects.select_related('user').all())).get(pk=self.kwargs['pk'])
        except Property.DoesNotExist:
            raise Http404
        ownerships = [owner.user for owner in property_owners.owners.all()]
        if not (self.request.user in ownerships) and self.request.method == "GET":
            raise exceptions.PermissionDenied
        return super(self.__class__, self).get(self, request, *args, **kwargs)

    def get_queryset(self):
        """
        Return new key with generated code
        """
        queryset = Key.objects.all()
        lock_id = self.kwargs.get('lock_id', None)
        queryset = queryset.filter(lock_id__tied_lock=lock_id)
        return queryset


