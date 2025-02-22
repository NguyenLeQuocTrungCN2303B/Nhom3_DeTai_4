from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.shortcuts import render
from django.urls import path
from django.db.models import Sum
from A_Product_Mng.models import Employee, Order, Product, OrderItem, Invoice, Customer, Counter, Promotion, Category
from django.contrib.auth.admin import UserAdmin

class CustomAdminSite(admin.AdminSite):
    site_header = "Quản lý cửa hàng trang sức"
    site_title = "Quản lý cửa hàng"
    index_title = "Bảng điều khiển"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(self.dashboard_view), name="admin_dashboard"),
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        """Tạo trang dashboard thống kê"""
        total_revenue = Invoice.objects.aggregate(Sum("order__orderitem__product__price"))["order__orderitem__product__price__sum"] or 0
        total_orders = Order.objects.filter(complete=True).count()
        total_products_sold = OrderItem.objects.aggregate(Sum("quantity"))["quantity__sum"] or 0
        total_employees = Employee.objects.count()
        total_customers = Customer.objects.count()
        total_counters = Counter.objects.count()
        
        revenue_by_employee = (
            Employee.objects.annotate(total_revenue=Sum("orders__orderitem__product__price"))
            .values("user__username", "total_revenue")
        )

        revenue_by_counter = (
            Counter.objects.annotate(total_revenue=Sum("employees__orders__orderitem__product__price"))
            .values("name", "total_revenue")
        )

        context = {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "total_products_sold": total_products_sold,
            "total_employees": total_employees,
            "total_customers": total_customers,
            "total_counters": total_counters,
            "revenue_by_employee": revenue_by_employee,
            "revenue_by_counter": revenue_by_counter,
        }
        return render(request, "admin/dashboard.html", context)

# Tạo Custom Admin Site
admin_site = CustomAdminSite(name="custom_admin")

# Unregister User & Group khỏi admin gốc
admin.site.unregister(User)
admin.site.unregister(Group)

# Đăng ký lại vào Custom Admin
admin_site.register(User, UserAdmin)
admin_site.register(Group)

# Đăng ký các model khác
admin_site.register(Employee)
admin_site.register(Order)
admin_site.register(Product)
admin_site.register(OrderItem)
admin_site.register(Invoice)
admin_site.register(Customer)
admin_site.register(Counter)
admin_site.register(Promotion)
admin_site.register(Category)
