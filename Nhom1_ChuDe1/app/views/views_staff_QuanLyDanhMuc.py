from django.shortcuts import render


def danh_muc_view(request):
    # Sau này dữ liệu từ Database sẽ được lấy ở đây
    return render(request, 'staff/QuanLyDanhMuc/QuanLyDanhMuc.html')