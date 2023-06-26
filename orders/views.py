from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings

import datetime
import requests as req

from store.models import Product
from cart.models import CartItem

from .forms import OrderForm
from .models import Order, Payment, OrderProduct

# Create your views here.

def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (13/100) * total
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data.get('first_name')
            data.last_name = form.cleaned_data.get('last_name')
            data.phone = form.cleaned_data.get('phone')
            data.email = form.cleaned_data.get('email')
            data.address_line_1 = form.cleaned_data.get('address_line_1')
            data.address_line_2 = form.cleaned_data.get('address_line_2')
            data.country = form.cleaned_data.get('country')
            data.state = form.cleaned_data.get('state')
            data.city = form.cleaned_data.get('city')
            data.order_note = form.cleaned_data.get('order_note')
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')#20230626
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total         
            }

            return render(request,'orders/payments.html', context=context)
    else:
        return redirect('checkout')
    
def payments(request):
    return render(request, 'orders/payments.html',)
    
def payment_success(request):
    
    amt = request.GET.get('amt')
    rid = request.GET.get('refId')
    pid = request.GET.get('oid')

    order = Order.objects.get(user = request.user, 
                              is_ordered = False,
                              order_number = pid,
                            )

    payment = Payment(
        user = request.user,
        payment_id = pid,
        payment_method = 'esewa',
        amount_paid = amt,
        status = "complete",
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # move the cart items ot order product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = item.product
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        order_product.save()
        order_product.variation.set(item.variation.all())

        # reduce product stock of the sold product
        product = item.product
        if product.stock > 0:
            product.stock -= item.quantity
            product.save()  
        else:
            return HttpResponse("Out of stock")
        
        # clear cart
        CartItem.objects.filter(user=request.user).delete()

        # send order received email to customer
        mail_subject = 'Order receipt'
        html_message = render_to_string('orders/order_confirm_email.html', {
            'user': request.user,
            'grand_total': amt,
            'trasaction_id': rid,
            'order_id': order.order_number,
            'order_date': order.updated_at
        })
        plain_message = strip_tags(html_message)
        to_email = request.user.email
        send_mail(
            mail_subject,
            plain_message,
            settings.EMAIL_HOST_USER,
            [to_email],
            html_message=html_message,
            fail_silently=False,
        )
        context = {
            'order': order,
            'order_items': order.orderproduct_set.all(),
        }
    return render(request, 'orders/payment_successful.html', context=context)

def payment_failure(request):
    return render(request, 'orders/payment_failure.html')