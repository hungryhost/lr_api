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


class AccountTypes(models.Model):
    acc_type = models.CharField(max_length=50, primary_key=True)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    CHOICES_1 = [
        ('ADMIN', 'Admin User'),
        ('STAFF', 'Staff User'),
        ('OWNER', 'Owner User'),
        ('CLIENT', 'Client User'),
        ('OTHER', 'Other User'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    account_type = models.CharField(max_length=300, choices=CHOICES_1, default="OWNER")
    is_confirmed = models.BooleanField(default=False)
    id_document = models.TextField(max_length=300)
    dob = models.DateField(null=True)
    main_address = models.TextField(max_length=200)
    patronymic = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)

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
    post_save.connect(create_profile, sender=User)


class UserLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    timestamp = models.DateTimeField()
    # action =
    # result =


class UserImages(models.Model):
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    filepath = models.CharField(max_length=200, null=False, blank=False)
    is_deleted = models.BooleanField(default=False)


class PhoneTypes(models.Model):
    phone_type = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=300, null=True, blank=True)


class Phones(models.Model):
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    phone_number = models.CharField(max_length=10, null=False, blank=False)
    phone_type = models.ForeignKey(PhoneTypes, on_delete=models.RESTRICT)
    is_deleted = models.BooleanField(default=False)
