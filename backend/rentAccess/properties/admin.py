from django.contrib import admin
from .models import Property
# Register your models here.
app = 'properties'
admin.site.register(Property)