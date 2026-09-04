import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from store.models import Order
from store.views import stripe_webhook


@login_required
@require_POST
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, paid=False)
    if not settings.STRIPE_SECRET_KEY.startswith(("sk_test_", "sk_live_")):
        return JsonResponse({"error": "A valid Stripe secret key is required."}, status=500)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": order.currency,
                    "product_data": {"name": f"Order #{order.id}"},
                    "unit_amount": int(order.total_amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri(
                "/payment_mgt/payment_success/"
            ) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/payment_mgt/payment_decline/"),
            client_reference_id=str(request.user.id),
            metadata={"user_id": str(request.user.id), "order_id": str(order.id)},
        )
    except stripe.error.StripeError as exc:
        return JsonResponse({"error": str(exc)}, status=502)
    return redirect(session.url)


def payment_success(request):
    return render(request, "payment_mgt/pay_success.html", {
        "session_id": request.GET.get("session_id"),
    })


def payment_decline(request):
    return render(request, "payment_mgt/payment_decline.html")


@csrf_exempt
def payment_success_webhook(request):
    return stripe_webhook(request)
