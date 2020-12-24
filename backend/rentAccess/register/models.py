from django.db import models
from datetime import datetime, date
from .validators import key_validator, card_validator
import uuid


# TODO: connection between locks and properties
# TODO: id fields can be deleted
# TODO: exact parameters in filter

class Lock(models.Model):
    """Model, representing locks in service.
    Fields:
        id (int): Internal read-only identifier.
        uuid (str): Identifier of the physical locks. Should hashes before saving.
        hash_id (str): Read-only hashed uuid. See function hash_lock_id from signals.py
        description (str): Lock description.
        is_on (bool): Required. Indicates, does locks close.
        is_approved (bool): Required. Is locks verified by superuser. Required to be True. False by default.
        last_echo (DateTime): Last time, when locks emitted echo. Used for connection monitoring.
    """
    id = models.BigAutoField('id', primary_key=True)
    uuid = models.UUIDField('uuid', default=uuid.uuid4, unique=True, editable=False)
    hash_id = models.CharField('hash_id', max_length=256, unique=True)
    description = models.TextField('description', blank=True, max_length=200, default="")
    is_on = models.BooleanField('is_on', null=False, default=True)
    is_approved = models.BooleanField('is_approved', default=True)
    last_echo = models.DateTimeField('last_echo', auto_now_add=True)

    def echo(self, save=False) -> None:
        """Marks response from locks.
        Should be used on every locks response.
        Args:
            save (bool): Save model immediately or later manually.
        """
        self.last_echo = datetime.utcnow()
        if save:
            self.save()

    @classmethod
    def get_instance_by_hash_id(cls, hash_id):
        """Finds locks by hashed uuid (exact match).
        Args:
            hash_id (str): given hashed uuid.
        Returns:
            Locks: Lock having that uuid.
        """
        return cls.objects.get(hash_id=hash_id.lower())


class Card(models.Model):
    """Model, representing RFID cards in service.
    Fields:
        id (int): Internal read-only identifier.
        card_id (str): Identifier of the physical RFID card. See card_validator. Should hashes before saving.
        hash_id (str): Read-only hashed card_id. See function hash_card_id from signals.py
        is_master (bool): Required. Indicates, does it master key.
        lock (Lock): Required. Lock for which access is given.
    """
    id = models.BigAutoField('id', primary_key=True)
    card_id = models.CharField('card', validators=[card_validator], unique=True, max_length=9)
    hash_id = models.CharField('hash_id', max_length=256, unique=True)
    is_master = models.BooleanField('is_master', null=False, default=False)
    lock = models.ForeignKey(Lock, models.CASCADE, 'lock_key',
                             null=False, verbose_name='lock_id',
                             db_index=True)

    @classmethod
    def get_instance_by_hash_id(cls, hash_id):
        """Finds card by hashed card_id.
        Args:
            hash_id (str): given hashed card_id.
        Returns:
            Card: object having that card_id.
        """
        return cls.objects.get(hash_id=hash_id.lower())


class Key(models.Model):
    """Model, representing keys for code panel in service.
    Fields:
        id (int): Internal read-only identifier.
        code (str): Generated code. See key_validator and function hash_code from signals.py. Should hashes before
        saving.
        hash_code (str): Read-only hashed code. See function hash_code from signals.py
        lock (Lock): Required. Lock for which access is given.
        access_start (Datetime): Required. Time when access to lock starts.
        access_stop (Datetime): Required. Time when access to lock ends.
    """
    id = models.BigAutoField('id', primary_key=True)
    code = models.PositiveIntegerField('code', validators=[key_validator], default=None,
                                       editable=False)
    hash_code = models.CharField('hash_code', max_length=256, unique=True)
    lock = models.ForeignKey(Lock, models.CASCADE, 'lock_code',
                             null=False, verbose_name='lock_id',
                             db_index=True)
    access_start = models.DateTimeField('access_start')
    access_stop = models.DateTimeField('access_stop')

    @classmethod
    def get_instance_by_hash_id(cls, hash_id):
        """Finds key by hashed uuid.
        Args:
            hash_id (str): given hashed code.
        Returns:
            Key: object having that code.

        """
        return cls.objects.get(hash_code=hash_id.lower())

