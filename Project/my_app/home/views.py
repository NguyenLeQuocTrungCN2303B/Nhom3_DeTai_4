from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from A_Product_Mng.models import *
import json
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
        order ={'get_cart_items':0,'get_cart_total':0}
    context = {'items': items, 'order': order}
    return render(request, 'home/shopping_cart.html', context)

def detail(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = None
    id = request.GET.get('id','')
    products =Product.objects.filter(id=id)
    context = {'items': items, 'order': order,'products':products}
    return render(request, 'home/detail.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)


def register(request):
    products = Product.objects.all()
    template = loader.get_template('home/register.html')
    context ={
        'products':products,
    }
    return HttpResponse(template.render(context,request))
def register(request):
    products = Product.objects.all()
    template = loader.get_template('home/register.html')
    context ={
        'products':products,
    }
    return HttpResponse(template.render(context,request))