from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quanLySanPham.urls')),
    path('', include('gioHang.urls')),
    path('don-dat/', include('donDat.urls')),
    path('', include('BaoCaoThongKe.urls')),
    path('', include('QuanLyDanhMuc.urls')),
    path('', include('quanLyDonHang.urls')),
    path('', include('quanLyKhachHang.urls')),
    path('', include('QuanLyKhuyenMai.urls')),
    path('', include('QuanLyNhaCungCap.urls')),
    path('', include('QuanLyNhapHang.urls')),
    path('accounts/', include('accounts.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
