from django.shortcuts import render
def khach_hang_view(request):
    return render(request, 'staff/QuanLyKhachHang/QuanLyKhachHang.html')
