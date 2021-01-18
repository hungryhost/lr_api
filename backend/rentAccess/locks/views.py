from rest_framework import response, decorators, permissions, status, generics
from django.core.exceptions import ObjectDoesNotExist
from .serializers import EchoSerializer

from .serializers import LockSerializer
from register.models import Lock


class LockDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LockSerializer
    queryset = Lock.objects.all()

    def get_queryset(self):
        """
        Return a lock determined by the id portion of the URL.
        """
        lock_id = self.kwargs['lock_id']
        return Lock.objects.filter(id=lock_id)


@decorators.api_view(["POST"])
@decorators.permission_classes([permissions.AllowAny])
def echo(request):
    """Handles service requests for monitoring connection to locks.
    Returns:
        Response: response with 200, 400 or 404 status.
    """
    serializer = EchoSerializer(data=request.data)
    if not serializer.is_valid():
        return response.Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    lock_id = request.data.get('id')
    try:
        lock = Lock.get_instance_by_hash_id(lock_id)
    except ObjectDoesNotExist:
        return response.Response(f'Lock with hash "{lock_id}" does not found', status=status.HTTP_404_NOT_FOUND)
    lock.echo(save=True)
    return response.Response(status=status.HTTP_200_OK)
