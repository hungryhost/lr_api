from django.dispatch import receiver
from django.db import models
from .models import UserImage


@receiver(models.signals.post_delete, sender=UserImage)
def remove_file_from_s3(sender, instance, using, **kwargs):
    instance.image.delete(save=False)
