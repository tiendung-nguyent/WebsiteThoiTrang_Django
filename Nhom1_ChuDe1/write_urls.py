import os

urls_files = {
    'BaoCaoThongKe/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/', views.bao_cao_view, name='bao_cao_staff'),\n]\n",
    'donDat/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('quan-ly-don-hang-user/', views.quanLyDonDat, name='quanLyDonDat'),\n]\n",
    'gioHang/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('gio-hang-user/', views.gio_hang, name='gioHang'),\n    path('thanh-toan/', views.thanh_toan_view, name='ThanhToan'),\n]\n",
    'QuanLyDanhMuc/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/QuanLyDanhMuc/', views.danh_muc_view, name='quanLyDM'),\n]\n",
    'quanLyDonHang/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/quanLyDonHang/', views.quanLyDonHang, name='quanLyDonHang'),\n    path('staff/quanLyDonHang/view/<str:status>/', views.view_quanLyDonHang, name='view_quanLyDonHang'),\n]\n",
    'quanLyKhachHang/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/QuanLyKhachHang/', views.khach_hang_view, name='quanLyKH'),\n]\n",
    'QuanLyKhuyenMai/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/khuyen-mai/', views.quan_ly_khuyen_mai_view, name='quan_ly_khuyen_mai'),\n]\n",
    'QuanLyNhaCungCap/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/nha-cung-cap/', views.quan_ly_ncc_view, name='quan_ly_ncc'),\n]\n",
    'QuanLyNhapHang/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('staff/quan-ly-nhap-hang/', views.nhap_hang_view, name='quan_ly_nhap_hang'),\n]\n",
    'quanLySanPham/urls.py': "from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('', views.trangChuUser, name='trangChuUser'),\n    path('user/', views.trangChuUser, name='index'),\n    path('staff/quanLySanPham/', views.quanLySP, name='quanLySP'),\n    path('staff/quanLySanPham/add/', views.add_quanLySP, name='add_quanLySP'),\n    path('staff/quanLySanPham/view/', views.view_quanLySP, name='view_quanLySP'),\n    path('staff/quanLySanPham/edit/', views.edit_quanLySP, name='edit_quanLySP'),\n    path('staff/quanLySanPham/delete/', views.delete_quanLySP, name='delete_quanLySP'),\n    path('san-pham-user/', views.chiTietSanPham, name='chiTietSanPham'),\n]\n",
}

for path, content in urls_files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done URLs!")
