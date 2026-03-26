from django.shortcuts import render


def khach_hang_view(request):
    # Sau này dữ liệu từ Database sẽ được lấy ở đây
    return render(request, 'staff/QuanLyKhachHang/QuanLyKhachHang.html')