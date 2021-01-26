from rest_framework import serializers
from register.models import Card, Key


class MasterKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'lock')


class KeyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ('id', 'lock', 'code', 'access_start', 'access_stop')


class KeyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ('id', 'lock', 'code', 'access_start', 'access_stop')


class KeyDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
