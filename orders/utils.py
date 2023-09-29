from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


from cart.models import CartItem
from .models import OrderProduct


def move_cart_items_to_ordered_items(request, order, payment, cart_items):
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


def send_order_received_mail(request, **kwargs):
    order = kwargs['order']
    mail_subject = 'Order receipt'
    html_message = render_to_string('orders/order_confirm_email.html', {
        'user': request.user,
        'grand_total': kwargs['amount'],
        'trasaction_id': kwargs['trasaction_id'],
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
