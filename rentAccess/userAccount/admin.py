from django.contrib import admin
from .models import (Profile, UserLogs, UserImages,
					Documents, DocumentTypes, AddressTypes,
					BillingAddresses)
from .models import Phones, PhoneTypes
# Register your models here.
admin.site.register(Profile)
admin.site.register(UserImages)
admin.site.register(UserLogs)
admin.site.register(PhoneTypes)
admin.site.register(Phones)
admin.site.register(DocumentTypes)
admin.site.register(Documents)
admin.site.register(AddressTypes)
admin.site.register(BillingAddresses)
