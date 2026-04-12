from django.shortcuts import render
def gio_hang(request):
    return render(request, 'user/gioHang/gio_hang.html')
def thanh_toan_view(request):
    return render(request, 'user/gioHang/ThanhToan.html')

def trangChuUser(request):
    return render(request, 'user/gioHang/trangChuUser.html')

def chiTietSanPham(request):
    return render(request, 'user/gioHang/chiTietSanPham.html')
