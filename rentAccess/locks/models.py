import os
from uuid import uuid4

from django.db import models
from register.models import Lock
# TODO: Возможно сюда следует перенести модель из register


def path_and_rename(instance, filename):
	path = ''
	ext = filename.split('.')[-1]
	# get filename
	if instance.pk:
		filename = '{}.{}'.format(instance.pk, ext)
	else:
		# set filename as random string
		filename = '{}.{}'.format(uuid4().hex, ext)
	# return the whole path to the file
	return os.path.join(path, filename)


class LockManuals(models.Model):
	class Meta:
		db_table = 'register_locks_manuals'

	file = models.FileField(upload_to=path_and_rename, blank=True, null=True)
	filename = models.CharField(max_length=255, null=False, blank=False)
	is_deleted = models.BooleanField(default=False)
	uploaded_at = models.DateTimeField(auto_now_add=True)


class LockWithManuals(models.Model):
	class Meta:
		db_table = 'register_locks_with_manuals'

	lock = models.ForeignKey(Lock, related_name='l_manuals',
	                         on_delete=models.CASCADE)
	manual = models.ForeignKey(LockManuals, related_name='m_manuals',
	                           on_delete=models.CASCADE)
	uploaded_at = models.DateTimeField(auto_now_add=True)


class LockGeneratedUserFiles(models.Model):
	class Meta:
		db_table = 'register_locks_user_files'

	lock = models.ForeignKey(Lock, related_name='user_files',
	                            on_delete=models.CASCADE)
	file = models.FileField(upload_to=path_and_rename, blank=True, null=True)
	filename = models.CharField(max_length=255, null=False, blank=False)
	is_deleted = models.BooleanField(default=False)
	uploaded_at = models.DateTimeField(auto_now_add=True)


