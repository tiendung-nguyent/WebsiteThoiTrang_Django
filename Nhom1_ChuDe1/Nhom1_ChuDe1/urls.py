from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('quanLySanPham.urls')),
    path('', include('gioHang.urls')),
    path('', include('donDat.urls')),
    path('', include('BaoCaoThongKe.urls')),
    path('', include('QuanLyDanhMuc.urls')),
    path('', include('quanLyDonHang.urls')),
    path('', include('QuanLyKhachHang.urls')),
    path('', include('QuanLyKhuyenMai.urls')),
    path('', include('QuanLyNhaCungCap.urls')),
    path('', include('QuanLyNhapHang.urls')),
]
