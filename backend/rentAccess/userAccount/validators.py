from django.core.validators import validate_email
from rest_framework import serializers


def email_validation(email):
    try:
        validate_email(email)
        return True
    except serializers.ValidationError:
        return False

