from rest_framework import serializers
from register.models import Lock


class EchoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lock
        fields = ('id',)
