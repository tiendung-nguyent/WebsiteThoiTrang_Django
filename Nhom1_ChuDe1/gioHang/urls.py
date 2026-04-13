from django.urls import path
from . import views

urlpatterns = [
    path('gio-hang-user/', views.gio_hang, name='gioHang'),
    path('thanh-toan/', views.thanh_toan_view, name='ThanhToan'),
    path('', views.trangChuUser, name='trangChuUser'),
    path('user/', views.trangChuUser, name='index'),
    path('san-pham-user/', views.chiTietSanPham, name='chiTietSanPham'),
]
