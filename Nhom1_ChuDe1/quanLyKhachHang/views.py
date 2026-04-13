from django.shortcuts import render, redirect, get_object_or_404
from .models import KhachHang, ChiTietKhachHang
from django.contrib import messages


def khach_hang_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # XÓA
        if action == "delete":
            ma = request.POST.get("KH_Ma")
            kh = get_object_or_404(KhachHang, KH_Ma=ma)
            kh.delete()

            messages.success(request, "Xóa khách hàng thành công")
            return redirect("quanLyKH")

    khach_hangs = KhachHang.objects.all()

    # Gắn thêm chi tiết
    for kh in khach_hangs:
        chi_tiet = ChiTietKhachHang.objects.filter(KH_Ma=kh).first()
        kh.so_dien_thoai = chi_tiet.CTKH_SDT if chi_tiet else ""
        kh.dia_chi = chi_tiet.CTKH_DiaChi if chi_tiet else ""
        kh.ten_nguoi_nhan = chi_tiet.CTKH_HoTenNguoiNhan if chi_tiet else kh.KH_Ten

    return render(request, "QuanLyKhachHang/QuanLyKhachHang.html", {
        "khach_hangs": khach_hangs
    })