from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
# Create your models here.
from common.models import PermissionLevels
from userAccount.models import *


class PropertyTypes(models.Model):
    r"""
    Property types are defined by following codes:
        - 100: Ordinary non-inhabitable property, like an office
        - 200: Inhabitable property, a flat or a house
    """
    property_type = models.IntegerField(primary_key=True, null=False, blank=False)
    description = models.CharField(max_length=150, null=False, blank=False)

    def __int__(self):
        return self.property_type


class Property(models.Model):
    VISIBILITY_CHOICES = [
        (100, 'Publicly Visible'),
        (200, 'Only within the organisation'),
        (300, 'Only owner and admins can see'),
    ]
    author = models.ForeignKey(User, related_name='properties', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField()
    price = models.PositiveIntegerField()
    visibility = models.IntegerField(choices=VISIBILITY_CHOICES, default=100)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    property_type = models.ForeignKey(PropertyTypes,
                to_field='property_type', related_name='property_types', on_delete=models.CASCADE)
    maximum_number_of_clients = models.IntegerField(default=1, null=False, blank=True)

    def __str__(self):
        return self.title


class Ownership(models.Model):
    VISIBILITY_CHOICES = [
        (100, 'Publicly Visible'),
        (150, 'Visible for those who booked the property'),
        (200, 'Only within the organisation scope'),
        (250, 'Only within the property owners scope'),
        (300, 'Only property initial owner and admins can see'),
    ]

    visibility = models.IntegerField(choices=VISIBILITY_CHOICES, default=100, null=False, blank=True)
    premises = models.ForeignKey(Property, related_name='owners', on_delete=models.CASCADE, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    is_initial_owner = models.BooleanField(default=False, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=False, blank=True)
    permission_level = models.ForeignKey(PermissionLevels, to_field='p_level',
                                         related_name='permission_levels',
                                         on_delete=models.CASCADE)
#    initial_owner_object = InitialOwnershipManager()


class PropertyLog(models.Model):
    listed_prop = models.ForeignKey(Property, on_delete=models.CASCADE)
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
    act_time = models.DateTimeField('act_time', null=False, auto_now_add=True)
    result = models.BooleanField('result', null=False)


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


class PremisesImages(models.Model):
    premises = models.ForeignKey(Property, to_field='id',
                                 related_name='property_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=path_and_rename, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_main = models.BooleanField(default=False)

    def set_main(self):
        self.is_main = True


class PremisesAddresses(models.Model):
    premises = models.OneToOneField(Property, related_name='property_address', on_delete=models.CASCADE,
                                 null=False, blank=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    street_1 = models.CharField(max_length=100, blank=False, null=False)
    street_2 = models.CharField(max_length=100, blank=True, null=False)
    building = models.CharField(max_length=20, blank=True, null=False)
    floor = models.CharField(max_length=20, blank=True, null=False)
    number = models.CharField(max_length=30, blank=True, null=False)
    zip_code = models.CharField(max_length=10, blank=True, null=False)
    directions_description = models.CharField(max_length=500, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class Bookings(models.Model):
    booked_from = models.DateTimeField(null=False, blank=False)
    booked_until = models.DateTimeField(null=False, blank=False)
    booked_property = models.ForeignKey(Property, related_name="booked_property",
                                        on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    client_email = models.EmailField(null=False, blank=True)
    number_of_clients = models.IntegerField(null=False, blank=True, default=1)
    STATUS_CHOICES = [
        ('ACCEPTED', 'Approved'),
        ('AWAITING', 'Awaiting action from the owner'),
        ('DECLINED', 'The owner declined the request')
    ]
    status = models.CharField(max_length=100, choices=STATUS_CHOICES,
                              null=False, blank=False, default='AWAITING')
    booked_by = models.ForeignKey(User, related_name="client_created_by",
                                    on_delete=models.CASCADE, null=True, blank=True)

