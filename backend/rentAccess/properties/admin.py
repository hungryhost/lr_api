from django.contrib import admin
<<<<<<< HEAD
from .models import Property
# Register your models here.
app = 'properties'
admin.site.register(Property)
=======
from .models import Property, PropertyLog
# Register your models here.
app = 'properties'
admin.site.register(Property)
admin.site.register(PropertyLog)
>>>>>>> backend-profile
