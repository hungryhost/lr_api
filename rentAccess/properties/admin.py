from django.contrib import admin
from .models import (Property, PropertyLog, Ownership, PremisesImage, PremisesAddress, PropertyType,
                     LockWithProperty, PermissionLevel, OwnershipPermission, OwnerPermission, Availability)
from bookings.models import Booking
# Register your models here.
app = 'properties'


class PropertiesMainAdmin(admin.ModelAdmin):
	list_display = ('listed_prop', 'user', 'action', 'act_time', 'result')


class PropertiesAdmin(admin.ModelAdmin):
	list_display = ('title', 'visibility', 'property_type')


admin.site.register(Property, PropertiesAdmin)
admin.site.register(OwnershipPermission)
admin.site.register(Availability)
admin.site.register(OwnerPermission)
admin.site.register(PremisesAddress)
admin.site.register(PermissionLevel)
admin.site.register(PropertyLog, PropertiesMainAdmin)
admin.site.register(Ownership)
admin.site.register(PremisesImage)
admin.site.register(PropertyType)
admin.site.register(Booking)
admin.site.register(LockWithProperty)

