from django.contrib import admin

# Register your models here.
from .models import AccessLog

admin.site.register(AccessLog)