from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from hashlib import sha1
from random import randint
from .models import Lock, Card, Key

MIN_CODE = 100000
"""int: the smallest number that can be code of key
"""
MAX_CODE = 999999999
"""int: the largest number that can be code of key
"""


@receiver(pre_save, sender=Lock, weak=False)
def hash_lock_id(sender: Lock.__class__, **kwargs):
    """Hashes uuid of lock just before saving it in database.
    """
    new_lock = kwargs['instance']
    new_lock.hash_id = sha1(str(new_lock.uuid).encode('utf-8')).hexdigest()


@receiver(pre_save, sender=Card, weak=False)
def hash_card_id(sender: Card.__class__, **kwargs):
    """Hashes card_id of card just before saving it in database.
    """
    new_card = kwargs['instance']
    new_card.hash_id = sha1(str(new_card.card_id).encode('utf-8')).hexdigest()


@receiver(pre_save, sender=Key, weak=False)
def hash_code(sender: Key.__class__, **kwargs):
    """Generates and saves a random number in the code field. Hashes generated code of key just before saving it in
    database.
    """
    new_key = kwargs['instance']
    new_key.code = randint(MIN_CODE, MAX_CODE)
    new_key.hash_code = sha1(str(new_key.code).encode('utf-8')).hexdigest()
