from rest_framework import generics, status
from .models import Lock, Card, Key
from locks.serializers import LockSerializer
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
    queryset = Card.objects.all()


class KeyList(generics.ListCreateAPIView):
    serializer_class = KeySerializer

    def get_queryset(self):
        """
        Return new key with generated code
        """
        queryset = Key.objects.all()
        key_id = self.request.query_params.get('id', None)
        queryset = queryset.filter(id=key_id)
        return queryset


