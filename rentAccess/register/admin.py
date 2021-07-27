from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import Key, Lock, Card, LockAPIKey, LockIPAddress

# Register your models here.

admin.site.register(Key)
admin.site.register(Lock)
admin.site.register(Card)
admin.site.register(LockIPAddress)

@admin.register(LockAPIKey)
class OrganisationAPIKeyModelAdmin(APIKeyModelAdmin):
    pass