from django.contrib import admin
from core.models import OrderItem, Order, Item, BillingAddress


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']


admin.site.register(Order, OrderAdmin)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(BillingAddress)
