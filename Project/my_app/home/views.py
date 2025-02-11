from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from A_Product_Mng.models import *
import requests 
import xml.etree.ElementTree as ET
# Create your views here.
def home(request):
    products = Product.objects.all()
    template = loader.get_template('home/index.html')
    context ={
        'products':products,
    }
    return HttpResponse(template.render(context,request))
def products(request):
    products = Product.objects.all()
    
    # Lấy dữ liệu giá vàng từ API
    gold_url = 'https://apiforlearning.zendvn.com/api/get-gold'
    gold_response = requests.get(gold_url, verify=False)
    items_gold = gold_response.json()
    
    # Tính toán giá bán của sản phẩm
    for product in products:
        product.price = (product.weight * float(items_gold[0]['sell'].replace(',', '')) + product.wage_price + product.Stone_price) * 1.3
        product.save()
    
    template = loader.get_template('home/products.html')
    context ={
        'products':products,
        'items_gold': items_gold,
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
#api giá vàng
def gold_price(request):
    gold_url = 'https://apiforlearning.zendvn.com/api/get-gold'
    gold_response = requests.get(gold_url, verify=False)
    items_gold = gold_response.json()
    return render(request , 'home/gold-price.html', {"items_gold": items_gold})


def shopping_cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = None
    context = {'items': items, 'order': order}
    return render(request, 'home/shopping_cart.html', context)