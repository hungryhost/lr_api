from django.contrib import admin
from .models import LockCatalogInfo, LockMessage, LockCatalogImages, LockAvailabilityStorage
# Register your models here.
admin.site.register(LockCatalogInfo)
admin.site.register(LockMessage)
admin.site.register(LockCatalogImages)
admin.site.register(LockAvailabilityStorage)