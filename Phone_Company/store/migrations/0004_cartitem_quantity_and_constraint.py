from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("store", "0003_alter_product_description_alter_product_price_and_more")]

    operations = [
        migrations.AlterField(
            model_name="cartitem",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddConstraint(
            model_name="cartitem",
            constraint=models.UniqueConstraint(fields=("user", "product"), name="unique_cart_item_per_user_product"),
        ),
    ]
