"""
URL configuration for Nhom1_ChuDe1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from app.views import views_user, views_staff, views_staff_quanLySanPham
urlpatterns = [
    path('admin/', admin.site.urls),

    # Đường dẫn cho Trang chủ User
    # SỬA DÒNG NÀY: Thay views_user.index bằng views_user.trangChuUser
    path('', views_user.trangChuUser, name='trangChuUser'),

    # Đảm bảo các dòng dưới cũng khớp với tên hàm trong views_user.py
    path('san-pham-user/', views_user.chiTietSanPham, name='chiTietSanPham'),
    path('gio-hang-user/', views_user.gio_hang, name='gioHang'),
    path('quan-ly-don-hang-user/', views_user.quanLyDonDat, name='quanLyDonDat'),
    path('staff/', views_staff.bao_cao_view, name='bao_cao_staff'),
    path('staff/quanLySanPham/', views_staff_quanLySanPham.quanLySP ,name='quanLySP'),
]
