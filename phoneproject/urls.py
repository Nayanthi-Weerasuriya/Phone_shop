"""URL configuration for the phoneproject project."""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
    path('store/', include('store.urls')),
    path('accounts/', include('user_accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('payment_mgt/', include(('payment_mgt.urls', 'payment_mgt'), namespace='payment_mgt')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
