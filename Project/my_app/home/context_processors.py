# your_app/context_processors.py
from A_Product_Mng.models import Category

def categories(request):
    categories = Category.objects.all()  # Lấy tất cả các danh mục
    return {
        'categories': categories  # Trả về dữ liệu cần thiết
    }
