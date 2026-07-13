"""Views for the store app."""

from django.shortcuts import render

# Create your views here.
def storehome(request):
    return render(request, 'store/storehome.html', {'title': 'Store Home'})

def aboutus(request):
    return render(request, 'store/aboutus.html', {'title': 'About Us'})

def reviews(request):
    return render(request, 'store/reviews.html', {'title': 'Reviews'})
