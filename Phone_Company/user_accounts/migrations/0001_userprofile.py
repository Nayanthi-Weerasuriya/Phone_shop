from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.FileField(blank=True, null=True, upload_to="profile_pictures/")),
                ("phone", models.CharField(blank=True, max_length=30)),
                ("address_line_1", models.CharField(blank=True, max_length=120)),
                ("address_line_2", models.CharField(blank=True, max_length=120)),
                ("city", models.CharField(blank=True, max_length=80)),
                ("state", models.CharField(blank=True, max_length=80)),
                ("country", models.CharField(blank=True, max_length=80)),
                ("zip_code", models.CharField(blank=True, max_length=20)),
                ("user", models.OneToOneField(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
