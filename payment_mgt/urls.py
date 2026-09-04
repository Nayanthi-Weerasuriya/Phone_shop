from django.urls import path

from . import views

app_name = "payment_mgt"

urlpatterns = [
    path(
        "create-checkout-session/<int:order_id>/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("payment_success/", views.payment_success, name="payment_success"),
    path("payment_decline/", views.payment_decline, name="payment_decline"),
    path(
        "payment_success_webhook/",
        views.payment_success_webhook,
        name="payment_success_webhook",
    ),
]
