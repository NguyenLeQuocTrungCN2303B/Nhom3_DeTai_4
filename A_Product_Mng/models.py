from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# Create your models here.
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
class Product (models.Model):
    name = models.CharField(max_length=225,null=True)
    kind = models.CharField(max_length=225,null=True)
    weight = models.FloatField()
    wage_price = models.FloatField()
    Stone_price= models.FloatField()
    price = models.FloatField(null=True, blank=True)
    detail= models.TextField(null=True, blank=True)
    digital = models.BooleanField(default=False,null=True, blank=False)
    image= models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    @property
    def total_price(self,gold_price):
        return (self.wage_price + self.Stone_price + self.weight*gold_price)

class Customer (models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=False)
    name = models.CharField(max_length=225)
    email= models.CharField(max_length=225)

    def __str__(self):
        return self.name

class Order (models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False,null=True, blank=False)
    transaction_id = models.CharField(max_length=225,null=True)

    def __str__(self):
        return str(self.id)
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
class OrderItem (models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress (models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=225,null=True)
    city = models.CharField(max_length=225,null=True)
    state = models.CharField(max_length=225,null=True)
    mobile = models.CharField(max_length=10,null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address


