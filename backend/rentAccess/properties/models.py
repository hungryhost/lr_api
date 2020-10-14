from django.db import models
from django.contrib.auth.models import User
# Create your models here.


# TODO: Update model for current schema

class Property(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	title = models.CharField(max_length=50)
	body = models.TextField()
	price = models.PositiveIntegerField()
	active = models.BooleanField(default=True)
	image = models.ImageField(upload_to='userpics/', blank=True, null=True)
	# lock_id

	def __str__(self):
		return self.title
