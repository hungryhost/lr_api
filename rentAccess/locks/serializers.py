from django.http import Http404
from rest_framework import serializers
from register.models import Lock
from properties.models import LockWithProperty


class EchoSerializer(serializers.ModelSerializer):
	class Meta:
		model = Lock
		fields = ('id',)


class LockSerializer(serializers.ModelSerializer):
	class Meta:
		model = Lock
		fields = ('id', 'uuid', 'description', 'is_on', 'is_approved')


class LockAndPropertySerializer(serializers.ModelSerializer):
	uuid = serializers.UUIDField(format='urn', source='lock.uuid', read_only=True)

	class Meta:
		model = LockWithProperty
		fields = ('id', 'uuid', 'description')


class AddLockToPropertySerializer(serializers.ModelSerializer):
	uuid = serializers.UUIDField(format='urn', source='lock.uuid', required=True)
	description = serializers.CharField(max_length=200, required=True)

	class Meta:
		model = LockWithProperty
		fields = ('id', 'uuid', 'description')
		read_only_fields = ['is_on', 'is_approved']

	def create(self, validated_data):

		uuid_ = validated_data["lock"]["uuid"]

		description = validated_data.get('description', None)
		try:
			lock = Lock.objects.get(uuid=uuid_)
		except Lock.DoesNotExist:
			raise Http404("Lock not found with such uuid.")
		if LockWithProperty.objects.filter(lock=lock).exists():
			raise serializers.ValidationError(
				{"Lock": "Lock with given uuid already used."}
			)
		lock_and_property = LockWithProperty.objects.create(lock=lock,
		                                                    property_id=self.context["property_id"],
		                                                    description=description)
		return lock_and_property
