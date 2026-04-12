from django.shortcuts import render
def nhap_hang_view(request):
    return render(request, 'staff/QuanLyNhapHang/QuanLyNhapHang.html')
