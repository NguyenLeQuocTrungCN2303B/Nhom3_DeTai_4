from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
from A_Product_Mng.models import *
import json 
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.db.models import Q
from django import template
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
import requests
import logging
import time
from django.contrib.auth.decorators import user_passes_test
from django.db.models.functions import TruncMonth
from django.core.exceptions import PermissionDenied
import xml.etree.ElementTree as ET
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
register = template.Library()

@register.filter
def indext(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'home/indext.html', context)

# Hàm lấy giá vàng từ API

logging.basicConfig(level=logging.INFO)

def get_gold_price():
    gold_url = "https://apiforlearning.zendvn.com/api/get-gold"

    for attempt in range(3):  # Thử tối đa 3 lần
        try:
            response = requests.get(gold_url, verify=False, timeout=10)
            response.raise_for_status()  # Kiểm tra lỗi HTTP
            
            data = response.json()

            # Kiểm tra dữ liệu hợp lệ
            if isinstance(data, list) and len(data) > 0 and "sell" in data[0]:
                sell_price = int(float(data[0]['sell'].replace(',', '')) * 1000000)  # Đổi sang đơn vị VND
                logging.info(f"✅ Giá vàng lấy được: {sell_price:,} VND")
                return sell_price

        except requests.exceptions.Timeout:
            logging.warning(f"⏳ Thử lần {attempt+1}: API timeout, đang thử lại...")
            time.sleep(2)  # Chờ 2 giây trước khi thử lại
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Lỗi API: {e}")
            break  # Nếu gặp lỗi không phải timeout thì dừng luôn

    logging.error("❌ API không phản hồi sau 3 lần thử. Trả về giá mặc định.")
    return 0

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
        if request.user.is_staff or request.user.is_superuser:
            # Admin không có Employee, nên không cần lấy employee
            order = None
            items = []
        else:
            try:
                employee = request.user.employee  # Truy cập Employee từ user
                order, created = Order.objects.get_or_create(employee=employee, complete=False)
                items = order.orderitem_set.all()  # Truy vấn các item trong đơn hàng
            except Employee.DoesNotExist:
                items = []
                order = None
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
        return redirect('indext')  # Nếu đã đăng nhập, chuyển hướng về trang chính

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Xác thực người dùng
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Đăng nhập vào Django
            request.session.set_expiry(0)  # Hết phiên làm việc sẽ đăng xuất
            return redirect('indext')  # Chuyển hướng sau khi đăng nhập thành công
        else:
            messages.error(request, 'Tài khoản hoặc mật khẩu không đúng!')
            return redirect('login')  # Tránh trường hợp đăng nhập sai vẫn ở lại trang

    return render(request, 'home/login.html')

def logoutPage(request):
    logout(request)
    return redirect('login')

def category(request):
    categories = Category.objects.all()
    active_category_slug = request.GET.get("category", None)
    products = Product.objects.none()  # Trả về QuerySet rỗng mặc định
    active_category = None  

    if active_category_slug:
        active_category = get_object_or_404(Category, slug=active_category_slug)
        products = Product.objects.filter(category=active_category).prefetch_related("category")  # Sửa lại

    context = {
        "categories": categories,
        "products": products,
        "active_category": active_category
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
    promotion = Promotion.objects.filter(start_date__lte=now(), end_date__gte=now()).first()
    return render(request, 'home/invoice_detail.html', {'invoice': invoice,'promotion': promotion})

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

def km(request):
    products = Product.objects.all()
    context = {
        'products': products,
    }
    return render(request, 'home/km.html', context)

def is_admin(user):
    return user.is_authenticated and user.is_staff  

def admin_dashboard(request):
    if not is_admin(request.user):
        raise PermissionDenied("Bạn không có quyền truy cập")

    # Tổng số liệu
    total_employees = Employee.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = Order.objects.filter(complete=True).aggregate(Sum('orderitem__product__price'))['orderitem__product__price__sum'] or 0

    # Doanh thu theo quầy
    revenue_by_counter = {counter: Order.objects.filter(employee__counter=counter, complete=True)
                          .aggregate(Sum('orderitem__product__price'))['orderitem__product__price__sum'] or 0
                          for counter in Counter.objects.all()}

    # Doanh thu theo nhân viên
    revenue_by_employee = {employee: Order.objects.filter(employee=employee, complete=True)
                           .aggregate(Sum('orderitem__product__price'))['orderitem__product__price__sum'] or 0
                           for employee in Employee.objects.all()}

    # Thống kê doanh thu theo tháng
    revenue_by_month = (
        Order.objects.filter(complete=True)
        .annotate(month=TruncMonth('date_ordered'))
        .values('month')
        .annotate(total=Sum('orderitem__product__price'))
        .order_by('month')
    )

    context = {
        "total_employees": total_employees,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "revenue_by_counter": revenue_by_counter,
        "revenue_by_employee": revenue_by_employee,
        "revenue_by_month": revenue_by_month,
    }
    return render(request, "admin/dashboard.html", context)

def employee_list(request):
    if not is_admin(request.user):
        raise PermissionDenied("Bạn không có quyền truy cập")

    employees = Employee.objects.select_related('user', 'counter').all()
    return render(request, 'home/employee_list.html', {'employees': employees})

def customer_list(request):
    if not is_admin(request.user):
        raise PermissionDenied("Bạn không có quyền truy cập")

    # Lấy danh sách khách hàng đã mua (có hóa đơn)
    customers = Customer.objects.filter(invoice__isnull=False).distinct()
    
    return render(request, 'home/customer_list.html', {'customers': customers})

def invoice_list(request):
    if not is_admin(request.user):
        raise PermissionDenied("Bạn không có quyền truy cập")

    invoices = Invoice.objects.all().order_by('-payment_date')
    return render(request, 'home/invoice_list.html', {'invoices': invoices})

def search_product(request):
    query = request.GET.get("q")  # Lấy từ khóa tìm kiếm từ URL
    products = Product.objects.all()

    if query:
        products = products.filter(Q(name__icontains=query))  # Tìm kiếm theo chuỗi con (không phân biệt chữ hoa/thường)

    return render(request, "home/search_results.html", {"products": products, "query": query})