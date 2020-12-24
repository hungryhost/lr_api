from rest_framework import serializers
from .models import Lock, Card, Key


class LockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lock
        fields = ('id', 'uuid', 'description', 'is_on', 'is_approved')


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'lock', 'card_id', 'is_master')


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ('id', 'lock', 'code', 'access_start', 'access_stop')

