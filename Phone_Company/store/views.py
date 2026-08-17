"""Views for browsing products and managing a signed-in user's cart."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import CartItem, Category, Product


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
