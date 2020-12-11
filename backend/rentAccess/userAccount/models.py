from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import os
from uuid import uuid4
#
#
#
#
#
#
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                primary_key=True, related_name='profile')
    CHOICES_1 = [
        ('CLIENT', 'Client User'),
        ('OTHER', 'Other User'),
    ]
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('', 'Not Set'),
    ]
    bio = models.CharField(null=False, blank=True, max_length=1024, default="")
    account_type = models.CharField(max_length=100, choices=CHOICES_1, default="OWNER")
    is_confirmed = models.BooleanField(default=False)
    dob = models.DateField(null=False, blank=True, default="1970-01-01")
    patronymic = models.CharField(max_length=50, null=False, blank=True, default="")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=False,
                              blank=True, default='')
    last_updated = models.DateTimeField(auto_now_add=True)

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
    class Meta:
        app_label = 'userAccount'
    user = models.ForeignKey(User, related_name='user_logs',
                             on_delete=models.RESTRICT)
    account = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    # action =
    # result =


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


class UserImages(models.Model):
    class Meta:
        app_label = 'userAccount'
    account = models.ForeignKey(User, related_name='account_images',
                                on_delete=models.CASCADE)
    image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class PhoneTypes(models.Model):
    class Meta:
        app_label = 'userAccount'
    phone_type = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.phone_type


class Phones(models.Model):
    class Meta:
        app_label = 'userAccount'
    account = models.ForeignKey(User, related_name='account_phones',
                                on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=13, null=False, blank=False)
    phone_type = models.ForeignKey(PhoneTypes, on_delete=models.RESTRICT)
    is_deleted = models.BooleanField(default=False)


class DocumentTypes(models.Model):
    class Meta:
        app_label = 'userAccount'
    doc_type = models.CharField(max_length=40, primary_key=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.doc_type


class AddressTypes(models.Model):
    class Meta:
        app_label = 'userAccount'
    addr_type = models.CharField(max_length=40, primary_key=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.addr_type


class Documents(models.Model):
    account = models.ForeignKey(User, related_name='documents', on_delete=models.CASCADE)
    doc_type = models.ForeignKey(DocumentTypes, to_field='doc_type', on_delete=models.CASCADE)
    doc_serial = models.PositiveIntegerField(null=True, blank=True, unique=True)
    doc_number = models.PositiveIntegerField(null=True, blank=True, unique=True)
    doc_issued_at = models.DateField(null=True, blank=True)
    doc_issued_by = models.CharField(max_length=100, blank=True, null=True)
    doc_is_confirmed = models.BooleanField(default=False)


class BillingAddresses(models.Model):
    class Meta:
        app_label = 'userAccount'
    account = models.ForeignKey(User, related_name='billing_addresses', on_delete=models.CASCADE)
    addr_type = models.ForeignKey(AddressTypes, on_delete=models.RESTRICT)
    addr_country = models.CharField(max_length=100, blank=True, null=True)
    addr_city = models.CharField(max_length=100, blank=True, null=True)
    addr_street_1 = models.CharField(max_length=100, blank=True, null=True)
    addr_street_2 = models.CharField(max_length=100, blank=True, null=True)
    addr_building = models.CharField(max_length=20, blank=True, null=True)
    addr_floor = models.CharField(max_length=20, blank=True, null=True)
    addr_number = models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True)
    addr_is_active = models.BooleanField(default=True)
