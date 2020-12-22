from django.contrib import admin
from .models import (Property, PropertyLog, Ownership, PremisesImages, PremisesAddresses, PropertyTypes,
					Bookings)
# Register your models here.
app = 'properties'
admin.site.register(Property)
admin.site.register(PremisesAddresses)
admin.site.register(PropertyLog)
admin.site.register(Ownership)
admin.site.register(PremisesImages)
admin.site.register(PropertyTypes)
admin.site.register(Bookings)

