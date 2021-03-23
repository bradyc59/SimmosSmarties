from django.contrib import admin

from .models import *

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(CaUser)
admin.site.register(ProductCategory)
