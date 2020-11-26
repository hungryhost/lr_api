from django.contrib.auth.models import User
from django.db import models

# TODO: separate docs and addresses into their own models
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
                                primary_key=True, related_name='user_profile')
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
    bio = models.CharField(null=True, blank=True)
    account_type = models.CharField(max_length=300, choices=CHOICES_1, default="OWNER")
    is_confirmed = models.BooleanField(default=False)
    dob = models.DateField(null=True, blank=True)
    patronymic = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True,
                              blank=True)

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
    uploaded_at = models.DateTimeField(auto_now_add=True)


class PhoneTypes(models.Model):
    phone_type = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=300, null=True, blank=True)


class Phones(models.Model):
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    phone_number = models.CharField(max_length=10, null=False, blank=False)
    phone_type = models.ForeignKey(PhoneTypes, on_delete=models.RESTRICT)
    is_deleted = models.BooleanField(default=False)


class DocumentTypes(models.Model):
    doc_type = models.CharField(max_length=40, primary_key=True)
    description = models.CharField(max_length=100, null=True, blank=True)


class AddressTypes(models.Model):
    addr_type = models.CharField(max_length=40, primary_key=True)
    description = models.CharField(max_length=100, null=True, blank=True)


class Documents(models.Model):
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    doc_type = models.ForeignKey(DocumentTypes, on_delete=models.RESTRICT)
    doc_serial = models.PositiveIntegerField(null=True, blank=True)
    doc_number = models.PositiveIntegerField(null=True, blank=True)
    doc_issued_at = models.DateField(null=True, blank=True)
    doc_issued_by = models.CharField(max_length=100, blank=True, null=True)
    doc_is_confirmed = models.BooleanField(default=False)


class BillingAddresses(models.Model):
    account = models.ForeignKey(Profile, on_delete=models.RESTRICT)
    addr_type = models.ForeignKey(AddressTypes, on_delete=models.RESTRICT)
    addr_country = models.CharField(max_length=100, blank=True, null=True)
    addr_city = models.CharField(max_length=100, blank=True, null=True)
    addr_street_1 = models.CharField(max_length=100, blank=True, null=True)
    addr_street_2 = models.CharField(max_length=100, blank=True, null=True)
    addr_building = models.CharField(max_length=20, blank=True, null=True)
    addr_floor = models.CharField(max_length=20, blank=True, null=True)
    addr_number = models.CharField(max_length=30, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True)
