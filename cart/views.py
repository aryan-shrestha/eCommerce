from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

from store.models import Variation
from store.models import Product
from cart.models import Cart, CartItem

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key

    if not cart:
        cart = request.session.create()

    return cart


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)        # getting selected product

    if current_user.is_authenticated:
        product_variation = []     
        if request.method == 'POST':
            for key in request.POST:
                value = request.POST[key]          
                try:                                        # getting selected variation
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)

                except:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()

        # create a new cart or increment quantity by 1 if already exist
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                for item in product_variation:
                    cart_item.variation.add(*product_variation)

        return redirect('cart')
    else:
        product_variation = []     
        if request.method == 'POST':
            for key in request.POST:
                value = request.POST[key]          
                try:                                        # getting selected variation
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)

                except:
                    pass

        # get cart if already exist or create a new cart   
        try:
            cart =  Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

        # create a new cart or increment quantity by 1 if already exist
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
        
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
            
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)
                item.save()

        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                cart = cart
            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                for item in product_variation:
                    cart_item.variation.add(*product_variation)
            
        cart.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:   
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    except:
        pass

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart') 

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (13/100) * total
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    context = {
    'total': total,
    'quantity': quantity,
    'cart_items': cart_items,
    'tax': round(tax, 2),
    'grand_total': grand_total
    }

    return render(request, 'store/cart.html', context=context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (13/100) * total
        grand_total = total + tax
    except Cart.DoesNotExist:
        pass

    context = {
    'total': total,
    'quantity': quantity,
    'cart_items': cart_items,
    'tax': round(tax, 2),
    'grand_total': grand_total
    }
    return render(request, 'store/checkout.html', context=context)
