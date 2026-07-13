"""Views for the store app."""

from django.shortcuts import render, get_object_or_404
from .models import Product, Category


def storehome(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'store/storehome.html', context)


def aboutus(request):
    return render(request, 'store/aboutus.html', {
        'title': 'About Us'
    })


def reviews(request):
    return render(request, 'store/reviews.html', {
        'title': 'Reviews'
    })


def product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    context = {
        'product': product,
    }

    return render(request, 'store/productinfo.html', context)