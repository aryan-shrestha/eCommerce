from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/", include('accounts.urls')),
    path("admin/", admin.site.urls),
    path("cart/", include('cart.urls')),
    path("store/", include('store.urls')),
    path("orders/", include("orders.urls")),
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()
