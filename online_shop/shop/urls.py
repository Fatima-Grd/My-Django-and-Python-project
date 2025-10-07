from django.urls import path
from .views import show_all_products, get_products, cart_view, order_view

urlpatterns = [
    path('show-all-products/', show_all_products, name='show_all_products'),
    path('products/', get_products, name='get_products'),
    path('cart/', cart_view, name='cart'),
    path('order/', order_view, name='order'),
]
