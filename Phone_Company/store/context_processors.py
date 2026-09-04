from .models import CartItem


def cart_item_count(request):
    """Make the signed-in user's cart count available to the shared navbar."""
    if not request.user.is_authenticated:
        return {"cart_item_count": 0}

    return {
        "cart_item_count": sum(
            CartItem.objects.filter(user=request.user).values_list("quantity", flat=True)
        )
    }
