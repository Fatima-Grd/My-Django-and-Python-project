from django.http import JsonResponse, HttpResponse
from .models import Product, ShoppingCart, Order

def show_all_products(request):
    # return HttpResponse("Your API is Work!")
    return JsonResponse({"result": "Your API is Work!"})

def get_products(request):
    products = Product.objects.all()
    return JsonResponse({"message": "Products"})

def cart_view(request):
    return JsonResponse({"message": "Cart"})

def order_view(request):
    return JsonResponse({"message": "Order"})



# Create your views here.
