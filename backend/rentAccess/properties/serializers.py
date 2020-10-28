from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Property
<<<<<<< HEAD

=======
>>>>>>> backend-profile
#
#


class PropertySerializer(serializers.ModelSerializer):
	class Meta:
<<<<<<< HEAD
		fields = ('author_id', 'id', 'title', 'body', 'price', 'active', 'image',)
		model = Property
=======
		model = Property
		author_id = serializers.Field(source='author')
		fields = ('author_id', 'id', 'title', 'body', 'price', 'active', 'image',)
		read_only_fields = ['author_id', 'id']





>>>>>>> backend-profile
