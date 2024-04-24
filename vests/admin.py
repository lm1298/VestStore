from django.contrib import admin
from .models import Vest, ShippingDetail, Order
# Register your models here.
admin.site.register(Vest)
admin.site.register(ShippingDetail)
admin.site.register(Order)