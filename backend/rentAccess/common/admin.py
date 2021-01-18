from .models import ActionTypes, ResultTypes, PermissionLevels
from django.contrib import admin

admin.site.register(ActionTypes)
admin.site.register(ResultTypes)
admin.site.register(PermissionLevels)