from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static
# Register your models here.
from A_Product_Mng.models import *
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Promotion)
admin.site.register(Counter)
admin.site.register(Employee)
admin.site.register(Invoice)
class CustomAdminSite(AdminSite):
    site_header = _("Quản lý cửa hàng trang sức")
    site_title = _("Trang Admin")
    index_title = _("Hệ Thống Quản Lý Cửa Hàng Báng Trang Sức")

    def each_context(self, request):
        """Thêm đường dẫn đến file CSS vào template"""
        context = super().each_context(request)
        context["custom_css"] = static("home/admin/css/custom_admin.css")  # Đường dẫn file CSS
        return context

admin.site = CustomAdminSite()
