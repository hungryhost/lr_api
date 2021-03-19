from hashlib import sha1
import random
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Organisation


def increment_helpdesk_number(name, reg):
    last_org = Organisation.objects.all().order_by('id').last()

    if not last_org:
        return name + '-' + '000001' + reg

    new_help_int = Organisation.objects.all().count() + 1
    new_help_id = name + '-' + str(new_help_int).zfill(6) + reg
    return new_help_id


@receiver(pre_save, sender=Organisation, weak=False)
def hash_card_id(sender: Organisation.__class__, **kwargs):
    """Hashes card_id of card just before saving it in database.
    """
    letters = ['A', 'B', 'C', 'D', 'E', 'F',
               'G', 'H', 'I', 'J', 'K', 'L',
               'M', 'N', 'O', 'P', 'Q', 'R',
               'S', 'T', 'U', 'V', 'W', 'X',
               'Y', 'Z']

    org = kwargs['instance']
    name_1 = random.choice(letters)
    name_2 = random.choice(letters)
    try:
        reg = org.organization_address.region
    except Exception as e:
        reg = "R00"
    org.LR_CRM_ID = increment_helpdesk_number(name_2+name_1, reg)
