import secrets

from django.db import models
from datetime import datetime, date

from django.db.models.signals import post_save
from rest_framework_api_key.models import AbstractAPIKey
from django.conf import settings

from .validators import key_validator, card_validator
import uuid
from encrypted_fields import fields


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
        linking_code(str): Generated code to link lock and property. See function create_linking_code from signals.py
    """
    VERSION_CHOICES = [
        (1, 'Ethernet'),
        (2, 'Wi-Fi'),
    ]
    FIRMWARE_CHOICES = [
        (1, '1'),
    ]
    id = models.BigAutoField('id', primary_key=True)
    uuid = models.UUIDField('uuid', default=uuid.uuid4, unique=True, editable=True)
    hash_id = models.CharField('hash_id', max_length=256, unique=True, blank=True, editable=True)
    description = models.TextField('description', blank=True, max_length=200, default="")
    is_on = models.BooleanField('is_on', null=False, default=True)
    is_approved = models.BooleanField('is_approved', default=True)
    last_echo = models.DateTimeField('last_echo', auto_now_add=True)
    version = models.IntegerField(choices=VERSION_CHOICES, default=1, null=False, blank=True)
    firmware = models.IntegerField(choices=FIRMWARE_CHOICES, default=1, null=False, blank=True)
    linking_code = models.TextField('linking_code', default=None, editable=True, null=True, blank=True, unique=True)

    class Meta:
        managed = True
        db_table = 'register_lock'

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
    _card_data = fields.EncryptedCharField(validators=[card_validator], null=False, max_length=9)
    card_id = fields.SearchField(hash_key=settings.CARD_HASH, encrypted_field_name='_card_data', editable=False)
    hash_id = models.CharField('hash_id', max_length=256, unique=False, editable=False)
    is_master = models.BooleanField('is_master', null=False, default=False)
    lock = models.ForeignKey(Lock, models.CASCADE, 'lock_key',
                             null=False, verbose_name='lock_id',
                             db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'register_card'

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
    _code_data = fields.EncryptedPositiveIntegerField(validators=[key_validator], null=False)
    code = fields.SearchField(hash_key=settings.KEY_HASH, encrypted_field_name='_code_data', editable=False)
    code_secure = models.TextField(editable=True, blank=True, null=False)
    hash_code = models.CharField('hash_code', max_length=256, unique=False, blank=True)
    lock = models.ForeignKey(Lock, models.CASCADE, 'lock_code',
                             null=False, verbose_name='lock_id',
                             db_index=True)
    access_start = models.DateTimeField('access_start')
    access_stop = models.DateTimeField('access_stop')
    created_manually = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'register_key'

    @classmethod
    def get_instance_by_hash_id(cls, hash_id):
        """Finds key by hashed uuid.
        Args:
            hash_id (str): given hashed code.
        Returns:
            Key: object having that code.

        """
        return cls.objects.get(hash_code=hash_id.lower())


class LockIPAddress(models.Model):
    class Meta:
        verbose_name = "Lock IP address"
        verbose_name_plural = "Lock IP addresses"
        db_table = 'register_lock_ip_addresses'

    lock = models.ForeignKey(
        Lock,
        on_delete=models.CASCADE,
        related_name="ip_addresses",
    )
    private_ip = models.CharField('private_ip', max_length=255)


class LockAPIKey(AbstractAPIKey):
    class Meta(AbstractAPIKey.Meta):
        db_table = "lock_api_keys"
        verbose_name = "Lock API key"
        verbose_name_plural = "Lock API keys"

    lock = models.ForeignKey(
        Lock,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
