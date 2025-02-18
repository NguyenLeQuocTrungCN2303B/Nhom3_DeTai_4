from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.timezone import now
from django.core.exceptions import ValidationError
# Create your models here.
class Category(models.Model):
    sub_category=models.ForeignKey('self',on_delete=models.CASCADE, related_name='sub_categories',null=True,blank=True)
    is_sub = models.BooleanField(default=False)
    name=models.CharField(max_length=200,null=True)
    slug=models.SlugField(max_length=200,unique=True)
    def __str__(self):
        return self.name
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
class Product (models.Model):
    barcode = models.CharField(max_length=100, unique=True, null=True, blank=True)
    category=models.ManyToManyField(Category,related_name='product')
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



class Order (models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
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
    @property
    def get_cart_total_after_discount(self):
        from .models import Promotion  # Tránh lỗi import tuần hoàn

        # Lấy khuyến mãi hợp lệ
        promotion = Promotion.objects.filter(apply_to_all=True, start_date__lte=now(), end_date__gte=now()).first()
        
        # Tính tổng tiền gốc
        total = self.get_cart_total
        
        # Nếu có khuyến mãi, giảm giá theo phần trăm
        if promotion:
            total *= (1 - promotion.discount_percentage / 100)

        return round(total, 2)  # Làm tròn 2 chữ số thập phân
  
class OrderItem (models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class Customer(models.Model):
    full_name = models.CharField(max_length=255)  # Tên khách hàng
    email = models.EmailField(unique=True)  # Email duy nhất
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Số điện thoại (không bắt buộc)

    def __str__(self):
        return self.full_name

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'email', 'phone_number']  # Các trường thông tin khách hàng


class Invoice(models.Model):
    """Mô hình hóa đơn với chi tiết sản phẩm"""
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, related_name="invoices")  # Liên kết với đơn hàng
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)  # Liên kết với khách hàn
    payment_date = models.DateTimeField(auto_now_add=True)  # Ngày thanh toán
    status = models.CharField(max_length=50, default='completed')  # Trạng thái thanh toán (completed, pending, etc.)

    @property
    def get_order_items(self):
        """Trả về các sản phẩm trong hóa đơn từ OrderItem"""
        return self.order.orderitem_set.all()
    

    





class Promotion(models.Model):
    name = models.CharField(max_length=255)  # Tên chương trình khuyến mãi
    description = models.TextField(blank=True, null=True)  # Mô tả khuyến mãi
    discount_percentage = models.FloatField()  # Giảm theo phần trăm
    start_date = models.DateTimeField()  # Ngày bắt đầu
    end_date = models.DateTimeField()  # Ngày kết thúc
    apply_to_all = models.BooleanField(default=True)  # Áp dụng cho toàn bộ sản phẩm

    class Meta:
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Promotion"

    def __str__(self):
        return f"{self.name} - {self.discount_percentage}%"

    def is_active(self):
        """Kiểm tra xem khuyến mãi có đang diễn ra hay không"""
        return self.start_date <= now() <= self.end_date

    def clean(self):
        """Kiểm tra dữ liệu trước khi lưu"""
        if self.end_date < self.start_date:
            raise ValidationError("Ngày kết thúc không thể trước ngày bắt đầu.")

    def save(self, *args, **kwargs):
        """Chặn tạo nhiều object"""
        if not self.pk and Promotion.objects.exists():
            raise ValidationError("Chỉ có thể có một chương trình khuyến mãi!")
        super().save(*args, **kwargs)
        
