from django.shortcuts import render
def danh_muc_view(request):
    return render(request, 'QuanLyDanhMuc/QuanLyDanhMuc.html')
