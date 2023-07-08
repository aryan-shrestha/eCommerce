from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache


from cart.models import CartItem
from orders.models import OrderProduct
from cart.views import _cart_id
from category.models import Category

from .forms import ReviewForm
from .models import Product, ProductGallery, ReviewRating

# Create your views here.

CACHE_TTL = getattr(settings , 'CACHE_TTL', DEFAULT_TIMEOUT)

def store(request, category_slug=None):
    """
    The `store` function retrieves products of given category from cache if avaiable, otherwise it queries the database.
    If category is not passed it retrieves all available products from cache if available, otherwise it queries the database.
    And then, paginates the products and renders them in the store template

    """
    categories = None
    products = None

    if category_slug != None:
        if cache.get(category_slug):
            products = cache.get(category_slug)
        else:
            categories = get_object_or_404(Category, slug=category_slug)
            products = Product.objects.filter(category=categories, is_available=True).order_by('price')
            cache.set(category_slug, products)
        
    else:
        if cache.get('all_products'):
            products = cache.get('all_products')
        else:
            products = Product.objects.all().filter(is_available=True).order_by('price')
            cache.set('all_products', products)

    products_count = products.count()
    paginator = Paginator(products, 6)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'products_count': products_count
    }

    return render(request, 'store/store.html', context=context)

def product_detail(request, category_slug, product_slug):
    
    if cache.get(f'{category_slug}_{product_slug}'):
        single_product = cache.get(f'{category_slug}_{product_slug}')
    else:
        try:
            single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
            in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
        except Exception as e:
            raise e

    if request.user.is_authenticated:
        try:
            order_product = OrderProduct.objects.filter(user=request.user, product=single_product).exists()
        except OrderProduct.DoesNotExist:
            order_product = None
    else:
        order_product = None

    reviews = ReviewRating.objects.filter(product=single_product, status=True)

    product_gallery = ProductGallery.objects.filter(product=single_product)
    
    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'order_product': order_product,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context=context)

def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            else:
                print('form invalid')
