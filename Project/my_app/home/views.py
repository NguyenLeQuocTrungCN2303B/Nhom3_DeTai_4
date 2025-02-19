from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from A_Product_Mng.models import *
import json 
import xml.etree.ElementTree as ET
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
import requests
from django.db.models import Q
from django import template

register = template.Library()

@register.filter
def indext(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'home/indext.html', context)


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
        return redirect('indext')  # Đảm bảo chuyển hướng đúng đến 'indext'
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('indext')  # Đảm bảo chuyển hướng sau khi đăng nhập thành công
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
            # Lấy category dựa trên tên (hoặc slug nếu bạn muốn)
            active_category = Category.objects.get(name=active_category_slug)
            # Truy vấn các sản phẩm có liên kết với active_category
            products = Product.objects.filter(category=active_category)  # Dùng 'category' thay vì 'Category'
        except Category.DoesNotExist:
            active_category = None
    
    context = {
        'categories': categories,
        'products': products,
        'active_category': active_category
    }
    return render(request, "home/category.html", context)

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

def create_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Lấy thông tin giỏ hàng từ shopping_cart
    if request.user.is_authenticated:
        employee = request.user.employee
        cart_order, created = Order.objects.get_or_create(employee=employee, complete=False)
        items = cart_order.orderitem_set.all()
        promotion = Promotion.objects.filter(start_date__lte=now(), end_date__gte=now()).first()
    else:
        items = []
        promotion = None  

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()  

            # Tạo hóa đơn với thông tin khách hàng và đơn hàng
            invoice = Invoice.objects.create(
                order=order,
                customer=customer,
                status="completed",
                payment_date=now()
            )

            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = CustomerForm()

    context = {
        'form': form,
        'order': order,
        'items': items,
        'promotion': promotion,
    }
    return render(request, 'home/create_invoice.html', context)

def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'home/invoice_detail.html', {'invoice': invoice})


from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from datetime import datetime

def generate_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    # Render HTML thành chuỗi
    html_string = render_to_string('home/invoice_pdf.html', {'invoice': invoice})

    # Tạo file PDF tạm thời
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        HTML(string=html_string).write_pdf(temp_file.name)

        # Đọc nội dung file PDF
        with open(temp_file.name, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

    # Trả về file PDF như HTTP response
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response



def category(request):
    categories=Category.objects.filter(is_sub=False)
    context = {
        'categories': categories,  # Truyền categories vào context
    }
    return render(request, "includes/left-menu.html", context)

def search_product(request):
    query = request.GET.get("q")  # Lấy từ khóa tìm kiếm từ URL
    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query))  # Tìm kiếm theo chuỗi con (không phân biệt chữ hoa/thường)

    return render(request, "home/search_results.html", {"products": products, "query": query})