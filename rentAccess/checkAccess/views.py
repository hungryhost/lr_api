from django.db.models import Prefetch
from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, generics, exceptions

from properties.models import Property, Ownership, LockWithProperty
from properties.permissions import IsOwner
from register.models import Card, Lock, Key
from .models import AccessLog
from .serializers import AccessListSerializer
char_accept = '#'
"""str: character that returns in response on accepted access attempt.

"""
char_denied = '*'
"""str: character that returns in response on refused access attempt.

"""


@api_view(['GET'])
def check_access_by_card(request):
    """Checks, if card from request has privilege to open lock.
    Detailed description provided in API documentation.
    Args:
        request (Request): Given request.
    Returns:
        Response: Response with char_access or char_denied and optional header "Error"
    See Also:
        https://www.django-rest-framework.org/api-guide/views/#function-based-views.
    """

    lock_id_hash: str = request.query_params.get('lock', None)
    card_id_hash: str = request.query_params.get('password', None)
    if not (lock_id_hash and card_id_hash):
        return Response('Provide "lock" and "password" query parameters',
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        lock = Lock.get_instance_by_hash_id(lock_id_hash.lower())
    except ObjectDoesNotExist as exc:
        return Response(char_denied, headers={'Error': str(exc)}, status=403)
    try:
        card = Card.get_instance_by_hash_id(card_id_hash.lower())
    except ObjectDoesNotExist as exc:
        return Response(char_denied, headers={'Error': str(exc)}, status=403)
    result = Card.objects.filter(lock=lock, hash_id=card_id_hash).exists()
    result_char = char_accept if result else char_denied
    lock.echo(save=True)
    return Response(result_char, status=200)


@api_view(['GET'])
def check_access_by_code(request):
    """Checks, if code from request has privilege to open lock.
    Detailed description provided in API documentation.
    Args:
        request (Request): Given request.
    Returns:
        Response: Response with char_access or char_denied and optional header "Error"
    See Also:
        https://www.django-rest-framework.org/api-guide/views/#function-based-views.
    """

    lock_id_hash: str = request.query_params.get('lock', None)
    hash_code: str = request.query_params.get('password', None)
    if not (lock_id_hash and hash_code):
        return Response('Provide "lock" and "pass" query parameters',
                        status=status.HTTP_400_BAD_REQUEST)
    now = datetime.utcnow()
    try:
        lock = Lock.get_instance_by_hash_id(lock_id_hash.lower())
    except ObjectDoesNotExist as exc:
        return Response(char_denied, headers={'Error': str(exc)}, status=403)
    try:
        key = Key.get_instance_by_hash_id(hash_code.lower())
    except ObjectDoesNotExist as exc:
        AccessLog.objects.create(result=False, is_failed=True, lock=lock.id, try_time=now, hash_code=hash_code)
        return Response(char_denied, headers={'Error': str(exc)}, status=403)
    result = Key.objects.filter(lock=lock, hash_code=hash_code, access_start__lte=now, access_stop__gte=now).exists()
    result_char = char_accept if result else char_denied
    lock.echo(save=True)
    AccessLog.objects.create(result=result, lock=lock.id, try_time=now, hash_code=hash_code)
    return Response(result_char, status=200)


class GetAccessList(generics.ListCreateAPIView):
    serializer_class = AccessListSerializer

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
        queryset = AccessLog.objects.all()
        lock_id = self.kwargs.get('lock_id', None)
        try:
            lock_with_property = LockWithProperty.objects.get(id=lock_id)
        except Exception:
            return Http404
        queryset = queryset.filter(lock=lock_with_property.lock.id)
        return queryset
