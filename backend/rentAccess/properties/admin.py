from django.contrib import admin
from .models import Property, PropertyLog
# Register your models here.
app = 'properties'
admin.site.register(Property)
admin.site.register(PropertyLog)