from django.contrib import admin
from .models import (Profile, AccountTypes, UserLogs, UserImages, Phones,
						PhoneTypes)

# Register your models here.
admin.site.register(Profile)
admin.site.register(AccountTypes)
admin.site.register(UserImages)
admin.site.register(UserLogs)
admin.site.register(PhoneTypes)
admin.site.register(Phones)
