from django.http import HttpResponse
from django.shortcuts import render
from store.models import ReviewRating

from store.models import Product


def home(request):
    products = Product.objects.all().filter(is_available=True)
    
    for product in products:
        reviews = ReviewRating.objects.filter(product=product, status=True)
    
    context = {
        'products': products
    }

    return render(request, 'home.html', context=context)
