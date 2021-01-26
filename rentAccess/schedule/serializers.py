from rest_framework import serializers
from register.models import Key


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ('id', 'access_start', 'access_stop')


class CheckScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ('id', 'lock', 'access_start', 'access_stop')