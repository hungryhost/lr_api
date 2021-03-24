from django.contrib import admin
from .models import (Property, PropertyLog, Ownership, PremisesImage, PremisesAddress, PropertyType,
                     LockWithProperty, PermissionLevel, Availability, FavoriteProperty, AvailabilityException,
Trip, TripMember, TripProperty

                     )
from bookings.models import Booking
# Register your models here.
app = 'properties'


class PropertiesMainAdmin(admin.ModelAdmin):
	list_display = ('listed_prop', 'user', 'action', 'act_time', 'result')


class PropertiesAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'visibility', 'property_type')


class AvailabilityAdmin(admin.ModelAdmin):
	list_display = ('id', 'premises')


admin.site.register(Property, PropertiesAdmin)
admin.site.register(Availability, AvailabilityAdmin)
admin.site.register(PremisesAddress)
admin.site.register(PermissionLevel)
admin.site.register(PropertyLog, PropertiesMainAdmin)
admin.site.register(Ownership, AvailabilityAdmin)
admin.site.register(PremisesImage, AvailabilityAdmin)
admin.site.register(PropertyType)
admin.site.register(Booking)
admin.site.register(LockWithProperty)
admin.site.register(FavoriteProperty)
admin.site.register(AvailabilityException)
admin.site.register(Trip)
admin.site.register(TripMember)
admin.site.register(TripProperty)



