from django.urls import path

from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payment/', views.payments, name='payments'),
    path('payment_successful/', views.payment_success, name='payment_success'),
    path('payment_failure/', views.payment_failure, name='payment_failure'),

    path('khalti-initiate/', views.initiate_khalti_payment,
         name='initiate_khalti_payment'),
    path('verify-khalti-payment/', views.verify_khalti_payment,
         name='verify_khalti_payment'),
]
