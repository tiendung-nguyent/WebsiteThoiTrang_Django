from django.urls import path
from . import views

urlpatterns = [
    path('gio-hang-user/', views.gio_hang, name='gioHang'),
    path('thanh-toan/', views.thanh_toan_view, name='ThanhToan'),
    path('', views.trangChuUser, name='trangChuUser'),
    path('', views.trangChuUser, name='trangChuUser'),
    path('san-pham/<str:sp_ma>/', views.chiTietSanPham, name='chiTietSanPham'),
    path('gio-hang/them/<str:sp_ma>/', views.them_vao_gio_hang, name='themVaoGioHang'),
]
