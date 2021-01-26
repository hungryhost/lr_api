import datetime
from time import timezone

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Documents, DocumentTypes


class DocumentsSerializer(serializers.ModelSerializer):
	doc_type = serializers.CharField(max_length=100, required=True)
	doc_serial = serializers.IntegerField(required=True)
	doc_number = serializers.IntegerField(required=True)
	doc_issued_at = serializers.DateField(required=True)
	doc_issued_by = serializers.CharField(max_length=100, required=True)
	doc_is_confirmed = serializers.BooleanField(read_only=True)

	class Meta:
		model = Documents
		fields = [
			'id',
			'account',
			'doc_type',
			'doc_serial',
			'doc_number',
			'doc_issued_at',
			'doc_issued_by',
			'doc_is_confirmed'
		]
		read_only_fields = ['id', 'account']

	def create(self, validated_data):
		# TODO: separate update mechanisms
		doc_type = DocumentTypes.objects.get(doc_type="passport_rus")
		obj = Documents.objects.create(
			account=self.context['request'].user,
			doc_type=doc_type,
			doc_serial=validated_data["doc_serial"],
			doc_number=validated_data["doc_number"],
			doc_issued_at=validated_data["doc_issued_at"],
			doc_issued_by=validated_data["doc_issued_by"]
		)
		return obj
