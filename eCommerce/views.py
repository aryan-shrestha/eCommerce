from django.shortcuts import render
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

from store.models import Product

CACHE_TTL = getattr(settings , 'CACHE_TTL', DEFAULT_TIMEOUT)

def home(request):
    """
    The `home` function retrieves a list of available products from the cache if available, otherwise it
    queries the database, sets the retrieved products in the cache, and returns a rendered template with
    the products as context.
    """

    if cache.get('home_products'):
        products = cache.get("home_products")
    else:
        products = Product.objects.all().filter(is_available=True)
        cache.set('home_products', products)

    context = {
        'products': products
    }

    return render(request, 'home.html', context=context)
