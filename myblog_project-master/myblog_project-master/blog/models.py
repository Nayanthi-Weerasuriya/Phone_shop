from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=75)
    category = models.CharField(max_length=100, null=True)
    content = models.TextField()

    def __str__(self):
        return self.title
