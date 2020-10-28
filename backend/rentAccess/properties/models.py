from django.db import models
<<<<<<< HEAD
from django.contrib.auth.models import User
# Create your models here.


# TODO: Update model for current schema

class Property(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
=======
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.
from userAccount.models import *

# TODO: Update model for current schema


class Property(models.Model):
	author = models.ForeignKey(Profile, on_delete=models.CASCADE)
>>>>>>> backend-profile
	title = models.CharField(max_length=50)
	body = models.TextField()
	price = models.PositiveIntegerField()
	active = models.BooleanField(default=True)
<<<<<<< HEAD
	image = models.ImageField(upload_to='userpics/', blank=True, null=True)
=======
	image = models.TextField(blank=True)
>>>>>>> backend-profile
	# lock_id

	def __str__(self):
		return self.title
<<<<<<< HEAD
=======


class PropertyLog(models.Model):
	listed_prop = models.ForeignKey(Property, on_delete=models.CASCADE)

	# lock_id =
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	CHOICES = [
		('POST', 'Post Request'),
		('PUT', 'PUT Request'),
		('PATCH', 'PATCH Request'),
		('DELETE', 'DELETE Request'),
		('DEACTIVATE', 'DEACTIVATE property'),
		('GIVE_ACC', 'Give access to property'),
	]
	action = models.CharField(max_length=300, choices=CHOICES)
	act_time = models.DateTimeField('act_time', null=False)
	result = models.BooleanField('result', null=False)

>>>>>>> backend-profile
