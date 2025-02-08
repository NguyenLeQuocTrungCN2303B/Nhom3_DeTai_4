from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from A_Product_Mng.models import Product
import requests 
# Create your views here.
def home(request):
   return render(request , 'home/index.html')

def products(request):
    products = Product.objects.all()
    template = loader.get_template('home/products.html')
    context ={
        'products':products,
    }
    return HttpResponse(template.render(context,request))

# chưa xong
def edit_product(request):
    product = Product.objects.get(id = 1)
    template = loader.get_template('home/product-edit.html')
    context ={
        'product':product,
    }
    return HttpResponse(template.render(context,request))

def gold_price(request):
    gold_url = 'https://apiforlearning.zendvn.com/api/get-gold'
    gold_response = requests.get(gold_url, verify=False)
    items_gold = gold_response.json()
    return render(request , 'home/gold-price.html', {"items_gold": items_gold})