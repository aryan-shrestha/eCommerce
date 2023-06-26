from django.contrib import admin

from .models import Payment, Order, OrderProduct

# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'user', 'product', 'quantity', 
                       'product_price', 'ordered', 'variation')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 
                    'order_total', 'status', 'is_ordered']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 
                     'email', 'phone', 'country', 'city', 'state', 
                     'address_line_1', 'address_line_2']
    list_per_page = 15
    inlines = [OrderProductInline]

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)