from django.contrib.auth.models import User
from django.db import models

# TODO: Rewrite Profile model to accommodate all required functionality
# TODO: add all required fields
#
#
#
#
#
#
#


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, blank=True)
    sec_name = models.CharField(max_length=255, blank=True)
    pat_name = models.CharField(max_length=255, blank=True)
    owner = models.BooleanField(default=True)
    #image = models.ImageField(default='default.jpg', upload_to='profile_pics',)
    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        self.user.delete()
        return super(self.__class__, self).delete(*args, **kwargs)