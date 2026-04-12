import os

files = {
    'BaoCaoThongKe/views.py': '''from django.shortcuts import render\ndef bao_cao_view(request):\n    return render(request, 'staff/BaoCaoThongKe/BaoCaoThongKe.html')\n''',
    'QuanLyKhuyenMai/views.py': '''from django.shortcuts import render\ndef quan_ly_khuyen_mai_view(request):\n    return render(request, 'staff/QuanLyKhuyenMai/QuanLyKhuyenMai.html')\n''',
    'QuanLyDanhMuc/views.py': '''from django.shortcuts import render\ndef danh_muc_view(request):\n    return render(request, 'staff/QuanLyDanhMuc/QuanLyDanhMuc.html')\n''',
    'quanLyDonHang/views.py': '''from django.shortcuts import render\ndef quanLyDonHang(request):\n    return render(request, 'staff/quanLyDonHang/quanLyDonHang.html')\ndef view_quanLyDonHang(request, status):\n    context = {'status': status, 'order_id': 'ORD-2026-001'}\n    return render(request, 'staff/quanLyDonHang/view_quanLyDonHang.html', context)\n''',
    'QuanLyKhachHang/views.py': '''from django.shortcuts import render\ndef khach_hang_view(request):\n    return render(request, 'staff/QuanLyKhachHang/QuanLyKhachHang.html')\n''',
    'QuanLyNhaCungCap/views.py': '''from django.shortcuts import render\ndef quan_ly_ncc_view(request):\n    return render(request, 'staff/QuanLyNhaCungCap/QuanLyNhaCungCap.html')\n''',
    'QuanLyNhapHang/views.py': '''from django.shortcuts import render\ndef nhap_hang_view(request):\n    return render(request, 'staff/QuanLyNhapHang/QuanLyNhapHang.html')\n''',
    'quanLySanPham/views.py': '''from django.shortcuts import render\ndef quanLySP(request):\n    return render(request, 'staff/quanLySanPham/quanLySanPham.html')\ndef add_quanLySP(request):\n    return render(request, 'staff/quanLySanPham/add_quanLySanPham.html')\ndef view_quanLySP(request):\n    return render(request, 'staff/quanLySanPham/view_quanLySanPham.html')\ndef edit_quanLySP(request):\n    return render(request, 'staff/quanLySanPham/edit_quanLySanPham.html')\ndef delete_quanLySP(request):\n    return render(request, 'staff/quanLySanPham/delete_quanLySanPham.html')\ndef trangChuUser(request):\n    return render(request, 'user/gioHang/trangChuUser.html')\ndef chiTietSanPham(request):\n    return render(request, 'user/gioHang/chiTietSanPham.html')\n''',
    'donDat/views.py': '''from django.shortcuts import render\ndef quanLyDonDat(request):\n    return render(request, 'user/donDat/quanLyDonDat.html')\n''',
    'gioHang/views.py': '''from django.shortcuts import render\ndef gio_hang(request):\n    return render(request, 'user/gioHang/gio_hang.html')\ndef thanh_toan_view(request):\n    return render(request, 'user/gioHang/ThanhToan.html')\n''',
}

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
print('Done!')
