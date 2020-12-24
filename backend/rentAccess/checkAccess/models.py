from django.db import models
from register.models import Lock, Key, Card


class Logs(models.Model):
    """Model, representing access attempts.
    Fields:
        lock (Lock): Locks uuid that was attempted to access.
        hash_code (str): Introduced hashed code.
        try_time (DateTime): Time when attempt was made.
        result (bool): Attempt result.
        is_failed (bool): Is there were any exceptions while checking attempt.
    """
    # lock = models.ForeignKey(Lock, models.CASCADE, 'l_logs', null=True,
    #                          verbose_name='l_id')
    lock = models.IntegerField('lock_id', default=0)
    hash_code = models.CharField('hash_code', max_length=256)
    try_time = models.DateTimeField('try_time', null=False)
    result = models.BooleanField('result', null=False)
    is_failed = models.BooleanField('is_failed', null=False, default=False)

    class Meta(object):
        ordering = ['-try_time']
        db_table = 'Logs'


