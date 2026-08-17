import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phoneproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from store.models import CartItem

User = get_user_model()
user = User.objects.filter(username='stripe_test_user').first()
if not user:
    print('test user not found')
    raise SystemExit(1)

print('initial cart count', CartItem.objects.filter(user=user).count())

client = Client()
# No need to login for webhook
payload = json.dumps({
    'type': 'checkout.session.completed',
    'data': {
        'object': {
            'client_reference_id': str(user.id),
        }
    }
})
resp = client.post('/stripe/webhook/', data=payload, content_type='application/json')
print('webhook status', resp.status_code)
print('final cart count', CartItem.objects.filter(user=user).count())
