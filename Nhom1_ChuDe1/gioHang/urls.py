from django.urls import path
from . import views

urlpatterns = [
    path('', views.trangChuUser, name='trangChuUser'),
    # ===== DANH SÁCH SẢN PHẨM =====
    path('san-pham/', views.danhSachSanPham, name='danhSachSanPham'),
    path('san-pham/<str:sp_ma>/', views.chiTietSanPham, name='chiTietSanPham'),
    path('gio-hang/them/<str:sp_ma>/', views.them_vao_gio_hang, name='themVaoGioHang'),
    path('gio-hang/', views.gio_hang, name='gioHang'),

    path('gio-hang/xoa/<int:ctgh_id>/', views.xoa_san_pham_khoi_gio, name='xoaSanPhamKhoiGio'),

    path('gio-hang/xoa-tat-ca/', views.xac_nhan_xoa_gio_hang, name='xacNhanXoaGioHang'),
    path('gio-hang/xoa-tat-ca/submit/', views.xoa_gio_hang, name='xoaGioHang'),

    path('gio-hang/cap-nhat/<int:ctgh_id>/', views.cap_nhat_san_pham_gio, name='capNhatSanPhamGio'),
    path('thanh-toan/', views.thanh_toan_view, name='ThanhToan'),
    path('gio-hang/tang/<int:ctgh_id>/', views.tang_so_luong_gio, name='tangSoLuongGio'),
    path('gio-hang/giam/<int:ctgh_id>/', views.giam_so_luong_gio, name='giamSoLuongGio'),
]