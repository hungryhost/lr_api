import re
from rest_framework.validators import ValidationError


def key_validator(value):
    """Validates if value contains only digits and has from 6 to 9 characters.
    Args:
        value (str) : Testing string.
    Raises:
        ValidationError: Error, occurred when string doesn't match the regular expression.
    """

    if not re.fullmatch(r'\d{6,9}', value):
        raise ValidationError('Code must contain only digits and have from 6 to 9 characters')


def card_validator(value):
    """Validates if value contains only latin characters and digits and has 6 characters.
    Args:
        value (str) : Testing string.
    Raises:
        ValidationError: Error, occurred when string doesn't match the regular expression.
    """

    if not re.fullmatch(r'[a-zA-Z\d]{6}', value):
        raise ValidationError('Card must contain only latin and digit character and have 6 characters')
