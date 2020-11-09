from django.contrib import admin
from .models import (Property, PropertyLog, Ownership, PremisesImages)
# Register your models here.
app = 'properties'
admin.site.register(Property)
admin.site.register(PropertyLog)
admin.site.register(Ownership)
admin.site.register(PremisesImages)
