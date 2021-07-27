from django.contrib import admin
from rest_framework_api_key.admin import APIKeyModelAdmin

from .models import Organisation, OrganisationMember, OrganisationAddress, OrganisationAPIKey
# Register your models here.
admin.site.register(Organisation)
admin.site.register(OrganisationMember)
admin.site.register(OrganisationAddress)


@admin.register(OrganisationAPIKey)
class OrganisationAPIKeyModelAdmin(APIKeyModelAdmin):
    pass