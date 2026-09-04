"""Views for browsing products and managing a signed-in user's cart."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import os
import stripe
import json
import logging
from decimal import Decimal
from django.utils import timezone
from django.db import transaction


from .models import CartItem, Category, Product, Order, ProcessedStripeEvent

logger = logging.getLogger(__name__)


def storehome(request):
    return render(request, "store/storehome.html", {
        "products": Product.objects.all(),
        "categories": Category.objects.all(),
    })


def home(request):
    return render(request, "store/home.html", {"products": Product.objects.all()})


def aboutus(request):
    return render(request, "store/aboutus.html", {"title": "About Us"})


def reviews(request):
    return render(request, "store/reviews.html", {"title": "Reviews"})


def productinfo(request, product_id):
    return render(request, "store/productinfo.html", {
        "product": get_object_or_404(Product, pk=product_id),
    })


@require_POST
@login_required(login_url="user_accounts:login_user")
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        quantity = max(1, int(request.POST.get("quantity", 1)))
    except (TypeError, ValueError):
        quantity = 1

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={"quantity": quantity},
    )
    if not created:
        CartItem.objects.filter(pk=cart_item.pk).update(quantity=F("quantity") + quantity)

    messages.success(request, f"{product.name} was added to your cart.")
    return redirect("view_cart")


@login_required(login_url="user_accounts:login_user")
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    total_price = sum((item.line_total for item in cart_items), start=0)
    return render(request, "store/shopping_cart.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })


@require_POST
@login_required(login_url="user_accounts:login_user")
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity <= 0:
        item.delete()
        messages.info(request, f"{item.product.name} was removed from your cart.")
    else:
        item.quantity = quantity
        item.save(update_fields=["quantity"])
        messages.success(request, "Cart quantity updated.")
    return redirect("view_cart")


@require_POST
@login_required(login_url="user_accounts:login_user")
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    product_name = item.product.name
    item.delete()
    messages.info(request, f"{product_name} was removed from your cart.")
    return redirect("view_cart")


# Stripe Checkout integration
@login_required(login_url="user_accounts:login_user")
@require_POST
def create_checkout_session(request):
    """Create a Stripe Checkout Session for the current user's cart and redirect to it.

    Uses per-session price_data so no pre-created Stripe Price is required.
    Requires STRIPE_SECRET_KEY in the environment.
    """
    cart_items = CartItem.objects.filter(user=request.user).select_related("product")
    if not cart_items:
        messages.info(request, "Your cart is empty.")
        return redirect("view_cart")

    stripe.api_key = settings.STRIPE_SECRET_KEY
    if not stripe.api_key or not stripe.api_key.startswith(("sk_test_", "sk_live_")) or len(stripe.api_key) <= 20:
        messages.error(request, "A valid Stripe secret key is required. Set STRIPE_SECRET_KEY in your .env file.")
        return redirect("view_cart")

    line_items = []
    total_price = sum((item.line_total for item in cart_items), start=Decimal("0.00"))
    order = Order.objects.create(
        user=request.user,
        total_amount=total_price,
        currency="usd",
        paid=False,
        metadata={"user_id": str(request.user.id)},
    )
    for item in cart_items:
        # Stripe expects integer cents
        unit_amount = int(round(item.product.current_price * 100))
        line_items.append({
            "price_data": {
                "currency": "usd",
                "unit_amount": unit_amount,
                "product_data": {
                    "name": item.product.name,
                },
            },
            "quantity": int(item.quantity),
        })

    success_url = request.build_absolute_uri(
        reverse("payment_mgt:payment_success")
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(reverse("payment_mgt:payment_decline"))

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(request.user.id),
            metadata={"user_id": str(request.user.id), "order_id": str(order.id)},
        )
    except stripe.error.AuthenticationError:
        messages.error(request, "Stripe rejected the secret key. Check STRIPE_SECRET_KEY in your .env file.")
        return redirect("view_cart")
    except Exception as e:
        messages.error(request, f"Unable to create Stripe Checkout session: {e}")
        return redirect("view_cart")

    # Redirect user to the Stripe hosted Checkout page
    return redirect(session.url)


@login_required(login_url="user_accounts:login_user")
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "store/order_list.html", {
        "orderlist": orders,
        "title": "My Orders",
    })


@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events. Clears the cart on successful Checkout completion.

    To verify signatures set STRIPE_WEBHOOK_SECRET in the environment and Stripe will
    send the 'Stripe-Signature' header which will be used to validate the payload.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    # Try to parse/validate the event
    try:
        if webhook_secret and sig_header:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            event = json.loads(payload)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event (work with both dicts and Stripe objects)
    # Normalize access to event type and session object in a safe way
    try:
        # event may be a dict (json.loads) or a Stripe Event object
        try:
            event_type = event["type"]
        except Exception:
            # fallback to attribute access
            event_type = getattr(event, "type", None)

        logger.info(f"Stripe webhook received: event_type={event_type}")

        # Determine event id for idempotency
        try:
            event_id = event["id"]
        except Exception:
            event_id = getattr(event, "id", None)

        # Idempotency: skip already-processed events
        if event_id:
            if ProcessedStripeEvent.objects.filter(event_id=event_id).exists():
                logger.info(f"Stripe event {event_id} already processed; skipping.")
                return HttpResponse(status=200)

        if event_type == "checkout.session.completed":
            try:
                # Access session object robustly
                try:
                    session = event["data"]["object"]
                except Exception:
                    # getattr(event, "data") may be a StripeObject without .get; handle safely
                    data_obj = getattr(event, "data", None)
                    if isinstance(data_obj, dict):
                        session = data_obj.get("object")
                    else:
                        # StripeObject: try indexing then attribute
                        try:
                            session = data_obj["object"] if data_obj is not None else None
                        except Exception:
                            session = getattr(data_obj, "object", None)

                def _get_session_field(sess, field, default=None):
                    if sess is None:
                        return default
                    if isinstance(sess, dict):
                        return sess.get(field, default)
                    # StripeObjects: prefer indexing then attribute
                    try:
                        return sess[field]
                    except Exception:
                        return getattr(sess, field, default)

                # Extract likely identifiers from session: client_reference_id, metadata.user_id, customer email
                client_ref = _get_session_field(session, "client_reference_id")
                if not client_ref:
                    metadata = _get_session_field(session, "metadata") or {}
                    # metadata may be a StripeObject as well
                    if not isinstance(metadata, dict):
                        try:
                            # try to convert by accessing keys
                            metadata = {k: metadata[k] for k in getattr(metadata, "keys", lambda: [])()} if metadata is not None else {}
                        except Exception:
                            metadata = {}
                    client_ref = metadata.get("user_id") or metadata.get("user") or client_ref

                # customer email fallback
                customer_email = None
                cust_email = _get_session_field(session, "customer_email")
                if cust_email:
                    customer_email = cust_email
                else:
                    cust_details = _get_session_field(session, "customer_details")
                    if isinstance(cust_details, dict):
                        customer_email = cust_details.get("email")
                    else:
                        # StripeObject customer_details
                        try:
                            customer_email = getattr(cust_details, "email", None)
                        except Exception:
                            customer_email = None

                logger.info(f"Stripe webhook session parsed: session_id={_get_session_field(session, 'id')}, client_ref={client_ref}, customer_email={customer_email}")

                # Resolve user by client_ref (prefer id) or by email as fallback
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = None
                if client_ref:
                    # client_ref may be numeric id or a string
                    try:
                        user = User.objects.get(id=int(client_ref))
                    except (ValueError, TypeError, User.DoesNotExist):
                        # try match by username or other identifier
                        try:
                            user = User.objects.get(username=str(client_ref))
                        except Exception:
                            user = None

                if user is None and customer_email:
                    try:
                        user = User.objects.get(email=customer_email)
                    except User.DoesNotExist:
                        user = None

                if user is None:
                    logger.warning("Webhook: could not resolve user from session (no client_ref or customer email). Session data keys: %s", list(session.keys()) if isinstance(session, dict) else getattr(session, "__dict__", {}).keys())
                else:
                    # Create order and mark as paid, and record the processed event id
                    with transaction.atomic():
                        # record processed event first for idempotency
                        if event_id:
                            ProcessedStripeEvent.objects.create(event_id=event_id)

                        metadata = _get_session_field(session, "metadata")
                        order_id = metadata.get("order_id") if isinstance(metadata, dict) else None
                        order = Order.objects.filter(
                            id=order_id,
                            user=user,
                            paid=False,
                        ).first() if order_id else None
                        if order is None:
                            order = Order.objects.create(user=user)
                        order.stripe_session_id = _get_session_field(session, "id") or None
                        order.stripe_event_id = event_id
                        order.total_amount = Decimal(_get_session_field(session, "amount_total", 0)) / Decimal(100)
                        order.currency = _get_session_field(session, "currency") or "usd"
                        order.paid = True
                        order.paid_at = timezone.now()
                        order.metadata = metadata if isinstance(metadata, dict) else None
                        order.save()

                        deleted, _ = CartItem.objects.filter(user=user).delete()
                        logger.info(f"Cleared {deleted} cart items for user id={getattr(user, 'id', None)}; created order id={order.id}")
            except Exception as exc:
                logger.exception('Error handling checkout.session.completed: %s', exc)
    except Exception as exc:
        logger.exception('Error processing webhook event: %s', exc)

    return HttpResponse(status=200)


def checkout_success(request):
    """Simple success page after returning from Stripe Checkout."""
    session_id = request.GET.get("session_id")
    return render(request, "store/checkout_success.html", {"session_id": session_id})


def checkout_cancel(request):
    """Simple cancel page if user cancels Checkout."""
    return render(request, "store/checkout_cancel.html" )
