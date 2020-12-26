from rest_framework import generics
from register.models import Key
from .serializers import ScheduleSerializer, CheckScheduleSerializer
import datetime
from rest_framework import status


# TODO: Check that access_start < access_stop
# TODO: Надо привязать расписание для замка не к id, а к uuid
# TODO: Возможно лучше принимать post запрос с датами и отправлять расписание в ответ, а не брать из url
# TODO: Рефакторинг

class AccessList(generics.ListCreateAPIView):
    serializer_class = CheckScheduleSerializer

    def get_queryset(self):
        """
        Return a list of all keys that are active in the period from the URL
        """
        year_s = self.kwargs['year_s']
        month_s = self.kwargs['month_s']
        day_s = self.kwargs['day_s']
        hour_s = self.kwargs['hour_s']
        min_s = self.kwargs['min_s']
        year_e = self.kwargs['year_e']
        month_e = self.kwargs['month_e']
        day_e = self.kwargs['day_e']
        hour_e = self.kwargs['hour_e']
        min_e = self.kwargs['min_e']
        return Key.objects.filter(access_start__lte=datetime.datetime(year_s, month_s, day_s, hour_s, min_s),
                                  access_stop__gte=datetime.datetime(year_e, month_e, day_e, hour_e, min_e))


class AccessDetail(generics.ListCreateAPIView):
    serializer_class = ScheduleSerializer

    def get_queryset(self):
        """
        Return a list of all bookings for
        the lock as determined by the lock_id portion of the URL.
        """
        lock_id = self.kwargs['pk']
        return Key.objects.filter(lock=lock_id)


class AccessNow(generics.ListCreateAPIView):
    serializer_class = CheckScheduleSerializer

    def get_queryset(self):
        """
        Return a list of all keys that are active now
        """
        return Key.objects.filter(access_start__lte=datetime.datetime.utcnow(),
                                  access_stop__gte=datetime.datetime.utcnow())
