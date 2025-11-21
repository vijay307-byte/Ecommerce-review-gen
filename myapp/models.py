
from django.db import models
from django.db.models import JSONField

class Review(models.Model):
    objects = None
    product_name = models.CharField(max_length=255)
    extra_input = models.TextField(blank=True, null=True)
    rating = models.IntegerField(default=5)
    title = models.CharField(max_length=255)
    pros = JSONField(default=list)
    cons = JSONField(default=list)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} Review"
