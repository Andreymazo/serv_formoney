from django.db import models

class Query(models.Model):
    title = models.CharField()
    price_total = models.DecimalField(max_digits=10, decimal_places=2)
    price_basic = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    views = models.IntegerField()
    article_uniq = models.CharField(unique=True)