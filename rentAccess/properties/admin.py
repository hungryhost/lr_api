from django.contrib import admin
from .models import (Property, PropertyLog, Ownership, PremisesImages, PremisesAddresses, PropertyTypes, LocksWithProperties)
from bookings.models import Bookings
# Register your models here.
app = 'properties'


class PropertiesMainAdmin(admin.ModelAdmin):
	list_display = ('listed_prop', 'user', 'action', 'act_time', 'result')


class PropertiesAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'visibility', 'property_type')


admin.site.register(Property, PropertiesAdmin)
admin.site.register(PremisesAddresses)
admin.site.register(PropertyLog, PropertiesMainAdmin)
admin.site.register(Ownership)
admin.site.register(PremisesImages)
admin.site.register(PropertyTypes)
admin.site.register(Bookings)
admin.site.register(LocksWithProperties)

