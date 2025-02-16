from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
from A_Product_Mng.models import *
import json
import requests 
import xml.etree.ElementTree as ET
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

def indext(request):
    categories=Category.objects.filter(is_sub=False)
    products = Product.objects.all()
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'home/index.html', context)


from django import template

register = template.Library()

@register.filter
def intcomma_custom(value):
    try:
        return f"{int(value):,}".replace(",", ".")  # Thay dấu `,` bằng `.`
    except (ValueError, TypeError):
        return value

# Hàm lấy giá vàng từ API


def get_gold_price():
    gold_url = 'https://apiforlearning.zendvn.com/api/get-gold'
    try:
        gold_response = requests.get(gold_url, verify=False, timeout=5)
        gold_response.raise_for_status()  # Kiểm tra lỗi HTTP
        items_gold = gold_response.json()

        if items_gold and "sell" in items_gold[0]:  
            # Chuyển đổi giá trị "sell" thành số nguyên
            return int(float(items_gold[0]['sell'].replace(',', '')))
    
    except (requests.RequestException, ValueError, IndexError, KeyError):
        return 0  # Giá mặc định nếu API lỗi
    
    return 0  # Trả về giá mặc định nếu có lỗi dữ liệu


# View xử lý danh sách sản phẩm
def products(request):
    products = Product.objects.all()
    gold_price = get_gold_price()

    updated_products = []
    for product in products:
        new_price = product.weight * gold_price + product.wage_price + product.Stone_price
        if product.price != new_price:  
            product.price = new_price
            updated_products.append(product)

    if updated_products:
        Product.objects.bulk_update(updated_products, ['price'])  

    
    template = loader.get_template('home/products.html')
    context = {
        'products': products,
        'gold_price': gold_price,
    }
    return HttpResponse(template.render(context, request))


def edit_product(request):
    product = Product.objects.get(id=1)
    template = loader.get_template('home/product-edit.html')
    context = {
        'product': product,
    }
    return HttpResponse(template.render(context, request))

def gold_price(request):
    gold_url = 'https://apiforlearning.zendvn.com/api/get-gold'
    gold_response = requests.get(gold_url, verify=False)
    items_gold = gold_response.json()
    return render(request, 'home/gold-price.html', {"items_gold": items_gold})

def shopping_cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(User=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
    context = {'items': items, 'order': order}
    return render(request, 'home/shopping_cart.html', context)

def detail(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(User=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items = []
        order = None
    id = request.GET.get('id', '')
    products = Product.objects.filter(id=id)
    context = {'items': items, 'order': order, 'products': products}
    return render(request, 'home/detail.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(User=customer, complete=False)
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
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form': form}
    return render(request, 'home/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Tài khoản hoặc mật khẩu không đúng!')
    return render(request, 'home/login.html', {})

def logoutPage(request):
    logout(request)
    return redirect('login')

def category(request):
    categories = Category.objects.all()
    active_category_slug = request.GET.get("category", None)
    products = []  
    active_category = None  
    if active_category_slug:
        try:
            active_category = Category.objects.get(name=active_category_slug)
            products = Product.objects.filter(Category=active_category)
        except Category.DoesNotExist:
            active_category = None
    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category
    }
    return render(request, "home/category.html", context)
