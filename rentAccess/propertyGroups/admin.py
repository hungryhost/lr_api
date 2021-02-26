from django.contrib import admin
from .models import PropertyGroup, PropertyGroupMembership, UserGroupMembership

# Register your models here.
admin.site.register(PropertyGroup)
admin.site.register(PropertyGroupMembership)
admin.site.register(UserGroupMembership)