"""URL configuration for the store app."""

from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('', views.storehome, name='storehome'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('reviews', views.reviews, name='reviews'),
    path('admin/', admin.site.urls),
    path('product', views.product, name='product'),
    path('product/<int:product_id>/', views.productinfo, name='productinfo'),
    


]
# Add static files support
urlpatterns += staticfiles_urlpatterns()
