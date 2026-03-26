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
from app.views import (views_user, views_staff,
                       views_staff_quanLySanPham,
                       views_staff_QuanLyNhapHang,
                       views_staff_QuanLyDanhMuc,
                       views_staff_QuanLyKhachHang,
                       views_staff_quanLyDonHang,
                       )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views_user.index,name='index'),
    path('user',views_user.index,name='index'),
    path('temp-url/', views_user.index, name='quanLyDonDat'),
    path('temp-url/', views_user.index, name='gioHang'),

    path('staff/', views_staff.bao_cao_view, name='bao_cao_staff'),
    path('staff/quanLySanPham/', views_staff_quanLySanPham.quanLySP ,name='quanLySP'),
    path('staff/quanLySanPham/add/', views_staff_quanLySanPham.add_quanLySP, name='add_quanLySP'),
    path('staff/quanLySanPham/view/', views_staff_quanLySanPham.view_quanLySP, name='view_quanLySP'),
    path('staff/quanLySanPham/edit/', views_staff_quanLySanPham.edit_quanLySP, name='edit_quanLySP'),
    path('staff/quanLySanPham/delete/', views_staff_quanLySanPham.delete_quanLySP, name='delete_quanLySP'),
    path('staff/quan-ly-nhap-hang/', views_staff_QuanLyNhapHang.nhap_hang_view, name='quan_ly_nhap_hang'),
    path('staff/QuanLyDanhMuc/', views_staff_QuanLyDanhMuc.danh_muc_view, name='quanLyDM'),
    path('staff/QuanLyKhachHang/', views_staff_QuanLyKhachHang.khach_hang_view, name='quanLyKH'),

    path('staff/quanLyDonHang/', views_staff_quanLyDonHang.quanLyDonHang, name='quanLyDonHang'),
    path('staff/quanLyDonHang/view/<str:status>/', views_staff_quanLyDonHang.view_quanLyDonHang, name='view_quanLyDonHang'),
]
