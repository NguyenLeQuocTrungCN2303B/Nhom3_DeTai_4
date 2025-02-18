from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from A_Product_Mng.models import *
import json
import requests 
import xml.etree.ElementTree as ET
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.utils.timezone import now
from home.utils import get_session_cart
from django import template
from A_Product_Mng.models import Product, Order, Promotion
def indext(request):
    categories=Category.objects.filter(is_sub=False)
    products = Product.objects.all()
    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'home/index.html', context)

  
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

def detail(request):
    # Lấy thông tin sản phẩm
    product_id = request.GET.get("id", "")
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(User=customer, complete=False)
        items = order.orderitem_set.all()
    else:
        items, order = get_session_cart(request)

    # Xử lý thêm sản phẩm vào giỏ hàng
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        if not product_id:
            messages.error(request, "Sản phẩm không hợp lệ!")
            return redirect("detail")

        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            order_item, created = order.orderitem_set.get_or_create(product=product)
            order_item.quantity += 1
            order_item.save()
        else:
            cart = request.session.get("cart", {})
            if product_id in cart:
                cart[product_id]["quantity"] += 1
            else:
                cart[product_id] = {
                    "quantity": 1,
                    "price": float(product.price),
                    "image": product.imageURL,
                    "detail": product.detail
                }

            request.session["cart"] = cart  
            request.session.modified = True  # Đảm bảo Django lưu session

        messages.success(request, "Sản phẩm đã được thêm vào giỏ hàng!")
        return redirect("shopping_cart")  # Chuyển hướng đến giỏ hàng

    # Trả dữ liệu về giao diện
    context = {"items": items, "order": order, "product": product}  
    return render(request, "home/detail.html", context)


def shopping_cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(User=customer, complete=False)
        items = order.orderitem_set.all()
        total_price = order.get_cart_total_after_discount  # Lấy tổng sau giảm giá
    else:
        items, order = get_session_cart(request)  # Dùng lại hàm có sẵn
        total_price = order.get("get_cart_total", 0)  # Lấy tổng tiền từ session

    # Kiểm tra khuyến mãi (nếu có)
    promotion = Promotion.objects.filter(start_date__lte=now(), end_date__gte=now()).first()

    context = {"items": items, "order": order, "promotion": promotion, "total_price": total_price}
    return render(request, "home/shopping_cart.html", context)


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

def detail(request):
    if request.user.is_authenticated:
        # Lấy thông tin nhân viên từ user hiện tại
        employee = request.user.employee  # Truy cập Employee từ user
        
        # Tạo hoặc lấy đơn hàng liên quan đến nhân viên đó và chưa hoàn thành
        order, created = Order.objects.get_or_create(employee=employee, complete=False)
        items = order.orderitem_set.all()  # Truy vấn các item trong đơn hàng
    else:
        items = []
        order = None

    id = request.GET.get('id', '')
    products = Product.objects.filter(id=id)
    context = {'items': items, 'order': order, 'products': products}
    return render(request, 'home/detail.html', context)




def shopping_cart(request):
    if request.user.is_authenticated:
        employee = request.user.employee  # Lấy thông tin nhân viên từ user
        order, created = Order.objects.get_or_create(employee=employee, complete=False)  # Thay User thành employee
        items = order.orderitem_set.all()
        promotion = Promotion.objects.filter(start_date__lte=now(), end_date__gte=now()).first()
    else:
        items = []
        order = {'get_cart_items': 0, 'get_cart_total': 0}
        promotion = None  # Không có khuyến mãi nếu chưa đăng nhập
    
    context = {'items': items, 'order': order, 'promotion': promotion}
    return render(request, 'home/shopping_cart.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    employee = request.user.employee  # Truy cập Employee từ user hiện tại
    product = Product.objects.get(id=productId)
    
    # Lấy hoặc tạo đơn hàng cho nhân viên đó và chưa hoàn thành
    order, created = Order.objects.get_or_create(employee=employee, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    # Thực hiện các hành động thêm hoặc giảm số lượng
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    
    # Lưu thay đổi vào orderItem
    orderItem.save()
    
    # Nếu số lượng <= 0, xóa item
    if orderItem.quantity <= 0:
        orderItem.delete()
    
    return JsonResponse('Item was updated', safe=False)


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


# nhân viên và quầy hàng 


def counter_list(request):
    counters = Counter.objects.all()
    return render(request, 'home/counter_list.html', {'counters': counters})


def counter_detail(request, counter_id):
    counter = get_object_or_404(Counter, id=counter_id)
    employees = counter.employees.all()  # Lấy danh sách nhân viên của quầy này
    return render(request, 'home/counter_detail.html', {'counter': counter, 'employees': employees})



def employee_checkout(request):
    # Kiểm tra nếu người dùng là nhân viên và có quyền thanh toán
    if not request.user.is_authenticated or not hasattr(request.user, 'employee'):

        return HttpResponse("Bạn không có quyền thanh toán", status=403)
    
    employee = request.user.employee  # Lấy đối tượng Employee của nhân viên
    if not employee.can_checkout:  # Kiểm tra xem nhân viên có quyền thanh toán không
        return HttpResponse("Bạn không có quyền thực hiện thanh toán", status=403)

    # Tìm đơn hàng chưa hoàn tất của người dùng
    order = Order.objects.filter(User=request.user, complete=False).first()
    
    if order:
        # Cập nhật trạng thái đơn hàng thành hoàn tất
        order.complete = True
        order.save()
        return HttpResponse("Thanh toán thành công")

    else:
        return HttpResponse("Không có đơn hàng để thanh toán")



def order_list(request):
    orders = Order.objects.all()  # Hoặc theo bất kỳ điều kiện nào bạn muốn
    context = {'orders': orders}
    return render(request, 'home/order_list.html', context)

def search_product_by_barcode(request):
    """API tìm kiếm sản phẩm theo barcode"""
    barcode = request.GET.get("barcode", "")
    product = Product.objects.filter(barcode=barcode).first()
    if product:
        return JsonResponse({"name": product.name, "price": product.price, "id": product.id})
    return JsonResponse({"error": "Không tìm thấy sản phẩm"}, status=404)




# views.py


def create_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()  # Lưu thông tin khách hàng vào database

            # Tạo hóa đơn với thông tin khách hàng và đơn hàng
            invoice = Invoice.objects.create(
                order=order,
                customer=customer,
                status="completed",
                payment_date=now()
            )

            # Chuyển hướng đến trang chi tiết hóa đơn
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = CustomerForm()

    return render(request, 'home/create_invoice.html', {'form': form, 'order': order})

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'home/invoice_detail.html', {'invoice': invoice})


    return HttpResponse("Không có đơn hàng để thanh toán")

