import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phoneproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from store.models import Product, CartItem, Category
from django.core.files import File

User = get_user_model()

USERNAME = 'stripe_test_user'
PASSWORD = 'testpass'

user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': 'stripe-test@example.com'})
if created:
    user.set_password(PASSWORD)
    user.save()

# Ensure there's a product
product = Product.objects.first()
if not product:
    cat, _ = Category.objects.get_or_create(name='Default')
    product = Product(name='Test Product', price=20.00, category=cat, description='Test product')
    # Attach an existing static image if available
    static_image_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'store', 'image.png')
    static_image_path = os.path.normpath(static_image_path)
    try:
        with open(static_image_path, 'rb') as f:
            product.image.save('test_image.png', File(f), save=False)
    except Exception:
        pass
    product.save()

# Clear existing cart items for user
CartItem.objects.filter(user=user).delete()

# Add one cart item
cart_item = CartItem.objects.create(user=user, product=product, quantity=1)

client = Client()
logged_in = client.login(username=USERNAME, password=PASSWORD)
print('logged_in', logged_in)

# Post to create-checkout-session
resp = client.post('/create-checkout-session/')
print('status_code', resp.status_code)
if 'Location' in resp:
    print('Location', resp['Location'])
else:
    # Django TestResponse may not have Location header if followed
    try:
        print('redirect_chain', resp.redirect_chain)
    except Exception:
        print('response_headers', resp.items())

# Also print current cart count
from store.models import CartItem
print('cart count for user', CartItem.objects.filter(user=user).count())
