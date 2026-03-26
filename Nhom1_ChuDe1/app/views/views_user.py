from django.shortcuts import render

def trangChuUser(request):
    # Trang này sẽ chứa danh sách sản phẩm nổi bật
    return render(request, 'user/gioHang/trangChuUser.html')

def chiTietSanPham(request):
    # Trang chi tiết sản phẩm
    return render(request, 'user/gioHang/chiTietSanPham.html')

def gio_hang(request):
    # Trang giỏ hàng
    return render(request, 'user/gioHang/gio_hang.html')

def quanLyDonDat(request):
    return render(request, 'user/donDat/quanLyDonDat.html')

def thanh_toan_view(request):
    return render(request, 'user/gioHang/ThanhToan.html')
