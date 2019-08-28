from django.contrib import admin
from core.models import OrderItem, Order, Item

admin.site.register(Order)
admin.site.register(Item)
admin.site.register(OrderItem)
