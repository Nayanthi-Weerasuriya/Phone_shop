"""URL configuration for the store app."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.storehome, name='store'),
    path('aboutus', views.aboutus, name='aboutus'),
    path('reviews', views.reviews, name='reviews'),
    path('shop/category/<slug:category_slug>/', views.storehome, name='products_by_category'),
    path('product/<int:product_id>/', views.productinfo, name='productinfo'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('cart/<int:item_id>/update/', views.update_cart, name='update_cart'),
    path('cart/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('shop/checkout/success/', views.checkout_success, name='checkout_success'),
    path('shop/checkout/cancel/', views.checkout_cancel, name='checkout_cancel'),

]
