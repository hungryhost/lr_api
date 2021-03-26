from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import Key, Lock, Card, LockAPIKey

# Register your models here.

admin.site.register(Key)
admin.site.register(Lock)
admin.site.register(Card)

@admin.register(LockAPIKey)
class OrganisationAPIKeyModelAdmin(APIKeyModelAdmin):
    pass