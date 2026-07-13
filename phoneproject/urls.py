"""URL configuration for the phoneproject project."""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from store import views as storeviews



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', storeviews.storehome),
    path('store/', include('store.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
