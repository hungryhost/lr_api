from __future__ import absolute_import
import os
import celery as cel
from celery.schedules import crontab
from django.conf import settings
from jwtauth.tasks import delete_blacklisted_tokens
import celery.signals

# set the default Django settings module for the 'celery_' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rentAccess.settings')
app = cel.Celery('rentAccess')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
	"""
	This method sets up periodic tasks.
	"""
	# handling of the periodic task that deletes all blacklisted tokens
	sender.add_periodic_task(crontab(minute=0, hour=0),
							 delete_blacklisted_tokens, name='delete_tokens_every_day')
