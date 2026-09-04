from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    """Additional contact and delivery details for a site user."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.FileField(upload_to="profile_pictures/", blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address_line_1 = models.CharField(max_length=120, blank=True)
    address_line_2 = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
