from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Property

#
#


class PropertySerializer(serializers.ModelSerializer):
	class Meta:
		fields = ('author_id', 'id', 'title', 'body', 'price', 'active', 'image',)
		model = Property
