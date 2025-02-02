from django.db import models

# Create your models here.
class Product (models.Model):
    name = models.CharField(max_length=225)
    kind = models.CharField(max_length=225)
    weight = models.FloatField()
class customer (models.Model):
    name = models.CharField(max_length=225)
    gender = models.BooleanField()
    birth_day=models.DateField()
