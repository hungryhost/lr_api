from rest_framework import serializers
from .models import Lock, Card, Key


class CardSerializer(serializers.ModelSerializer):
    manufacturing_id = serializers.IntegerField(source='lock.id')

    class Meta:
        model = Card
        fields = ('id', 'manufacturing_id', 'card_id', 'is_master')


class KeySerializer(serializers.ModelSerializer):
    manufacturing_id = serializers.IntegerField(source='lock.id')

    class Meta:
        model = Key
        fields = ('id', 'manufacturing_id', 'code', 'access_start', 'access_stop')

