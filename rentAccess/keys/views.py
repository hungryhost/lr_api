from rest_framework import generics
from .serializers import MasterKeySerializer, KeyUpdateSerializer, KeyDeleteSerializer, KeyDetailSerializer
from register.models import Card, Key


# TODO: Add permissions


class MasterKeyList(generics.ListAPIView):
    queryset = Card.objects.filter(is_master=True)
    serializer_class = MasterKeySerializer


class MasterKeyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Card.objects.filter(is_master=True)
    serializer_class = MasterKeySerializer


class KeyUpdate(generics.UpdateAPIView):
    queryset = Key.objects.filter()
    serializer_class = KeyUpdateSerializer

    def get_queryset(self):
        """
        Return a lock determined by the id portion of the URL.
        """
        key_id = self.kwargs['pk']
        return Key.objects.filter(id=key_id)


class KeyDelete(generics.DestroyAPIView):
    queryset = Key.objects.filter()
    serializer_class = KeyDeleteSerializer

    def get_queryset(self):
        """
        Return a lock determined by the id portion of the URL.
        """
        key_id = self.kwargs['pk']
        return Key.objects.filter(id=key_id)


class KeyDetail(generics.RetrieveAPIView):
    queryset = Key.objects.filter()
    serializer_class = KeyDetailSerializer

    def get_queryset(self):
        """
        Return a lock determined by the id portion of the URL.
        """
        key_id = self.kwargs['pk']
        return Key.objects.filter(id=key_id)
