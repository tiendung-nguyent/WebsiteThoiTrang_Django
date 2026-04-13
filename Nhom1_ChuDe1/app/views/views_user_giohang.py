from django.shortcuts import render, redirect

def trangChuUser(request):
    return render(request, 'user/gioHang/trangChuUser.html')

def chiTietSanPham(request):
    return render(request, 'user/gioHang/chiTietSanPham.html')

def gio_hang(request):
    return render(request, 'user/gioHang/gio_hang.html')

def xoa_gio_hang(request):
    # xử lý xóa giỏ (tạm thời redirect)
    return redirect('gioHang')