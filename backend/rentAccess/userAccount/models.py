from django.contrib.auth.models import User
from django.db import models

# TODO: Rewrite Profile model to accommodate all required functionality
# TODO: add all required fields
# TODO: add read only and extra fields/validation
#
#
#
#
#
#
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
<<<<<<< HEAD
    owner = models.BooleanField(default=True)
    #image = models.ImageField(default='default.jpg', upload_to='profile_pics',)
=======
    CHOICES = [
        ('ADMIN', 'Admin User'),
        ('STAFF', 'Staff User'),
        ('OWNER', 'Owner User'),
        ('CLIENT', 'Client User'),
        ('OTHER', 'Other User'),
    ]
    account_type = models.CharField(max_length=300, choices=CHOICES, default="OWNER")
    # image = models.ImageField(default='default.jpg', upload_to='profile_pics',)
>>>>>>> backend-profile

    def __str__(self):
        return self.user.username

    def delete(self, *args, **kwargs):
        self.user.delete()
        return super(self.__class__, self).delete(*args, **kwargs)

    def create_profile(sender, **kwargs):
        user = kwargs["instance"]
        if kwargs["created"]:
            user_profile = Profile(user=user)
            user_profile.save()
<<<<<<< HEAD
    post_save.connect(create_profile, sender=User)
=======
    post_save.connect(create_profile, sender=User)


class UserLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    
>>>>>>> backend-profile
