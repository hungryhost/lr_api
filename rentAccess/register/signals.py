import datetime
import secrets

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from hashlib import sha1
from random import randint
from .models import Lock, Card, Key
from django.core import signing
from django.core.signing import Signer
MIN_CODE = 100000
"""int: the smallest number that can be code of key
"""

MIN_LINKING_CODE = 10000
"""int: the smallest number that can be linking code of lock
"""

MAX_LINKING_CODE = 99999
"""int: the largest number that can be linking code of lock
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


def secure_code(key: Key, code: int):
    data_to_sign = {
        "code": code,
        "expires_at_dt": key.access_stop.strftime('%Y-%m-%dT%H:%M:%S%z'),
        "expires_seconds": str((key.access_stop - key.access_start).total_seconds()),
        "lock_id": key.lock.id,
        "signed_at": datetime.datetime.now().timestamp()
    }
    return signing.dumps(data_to_sign)


@receiver(post_save, sender=Lock, weak=False)
def create_linking_code(sender: Lock.__class__, instance, created, **kwargs):
    """Generates and saves a random number in the linking_code field just before saving lock in database.
    """
    if created:
        new_lock = instance
        #print(new_lock)
        id_string = str(new_lock.id)
        #print(id_string)
        # Define our random string alphabet (notice I've omitted I,O,etc. as they can be confused for other characters)
        upper_alpha = "ABCDEFGHJKLMNPQRSTVWXYZ"
        # Create an 8 char random string from our alphabet
        random_str = "".join(secrets.choice(upper_alpha) for i in range(8))
        # Append the ID to the end of the random string
        new_lock.linking_code = (random_str + id_string)[-8:]
        new_lock.save()


@receiver(pre_save, sender=Key, weak=False)
def hash_code(sender: Key.__class__, **kwargs):
    """Generates and saves a random number in the code field. Hashes generated code of key just before saving it in
    database.
    """
    new_key = kwargs['instance']
    if not new_key.code:
        code = randint(MIN_CODE, MAX_CODE)
        new_key.code = code
    else:
        code = new_key.code
        new_key.created_manually = True
    new_key.code_secure = secure_code(new_key, code)
    new_key.hash_code = sha1(str(code).encode('utf-8')).hexdigest()
