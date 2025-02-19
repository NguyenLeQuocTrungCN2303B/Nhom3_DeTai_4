from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('A_Product_Mng.urls')),
    path('', include('home.urls')),
    path('admin/', admin.site.urls),  # Đảm bảo dòng này không bị ghi đè
]

# Chỉ thêm static nếu đang chạy ở chế độ DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
