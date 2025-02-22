from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from home.admin import admin_site
urlpatterns = [
    path('products/', include('A_Product_Mng.urls')), 
    path('admin/', admin_site.urls),
    path('', include('home.urls')),  # Trang chủ
    
]

# Chỉ thêm static nếu đang chạy ở chế độ DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
