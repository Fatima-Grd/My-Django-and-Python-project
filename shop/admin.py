from django.contrib import admin
from .models import Product, ShoppingCart, CartItem, Order, OrderItem

admin.site.register(Product)
admin.site.register(ShoppingCart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)


# Register your models here.
