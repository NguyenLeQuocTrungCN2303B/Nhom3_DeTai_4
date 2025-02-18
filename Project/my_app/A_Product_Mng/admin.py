from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Promotion)
admin.site.register(Counter)
admin.site.register(Employee)
admin.site.register(Invoice)

