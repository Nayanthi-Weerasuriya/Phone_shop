from django.db import models
from django.contrib.auth.models import User

# Categories of Products
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


# All of our Products
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=1250, default='', blank=True, null=True)
    more_info = models.TextField(max_length=1000, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    # Add Sale Stuff
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
   
    def __str__(self) -> str:
        return self.name

    @property
    def current_price(self):
        return self.sale_price if self.is_sale else self.price



class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    purchase = models.BooleanField(default=True)


    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    @property
    def line_total(self):
        return self.product.current_price * self.quantity

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "product"), name="unique_cart_item_per_user_product"),
        ]
