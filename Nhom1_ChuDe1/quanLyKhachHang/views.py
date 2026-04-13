from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum

from accounts.models import Profile
from donDat.models import DonDat
from .models import ChiTietKhachHang


def khach_hang_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # Xóa theo mã chi tiết khách hàng
        if action == "delete":
            ctkh_ma = request.POST.get("KH_Ma")
            chi_tiet = get_object_or_404(ChiTietKhachHang, CTKH_Ma=ctkh_ma)
            chi_tiet.delete()
            messages.success(request, "Xóa khách hàng thành công.")
            return redirect("quanLyKH")

    khach_hangs = []

    # Lấy danh sách chi tiết khách hàng đang được dùng trong đơn đặt
    chi_tiet_ids = DonDat.objects.values_list("CTKH_Ma_id", flat=True).distinct()

    for ctkh_id in chi_tiet_ids:
        chi_tiet = ChiTietKhachHang.objects.filter(CTKH_Ma=ctkh_id).first()
        if not chi_tiet:
            continue

        # Match qua số điện thoại
        profile = Profile.objects.select_related("user").filter(
            phone_number=chi_tiet.CTKH_SDT
        ).first()

        don_hangs = DonDat.objects.filter(CTKH_Ma=chi_tiet)

        so_don_hang = don_hangs.count()
        tong_chi_tieu = don_hangs.aggregate(
            tong=Sum("TT_TongThanhToan")
        )["tong"] or 0

        ho_ten = profile.user.username if profile else chi_tiet.CTKH_HoTenNguoiNhan
        so_dien_thoai = profile.phone_number if profile else chi_tiet.CTKH_SDT
        dia_chi = chi_tiet.CTKH_DiaChi

        khach_hangs.append({
            "KH_Ma": chi_tiet.CTKH_Ma,
            "ho_ten": ho_ten,
            "so_dien_thoai": so_dien_thoai,
            "dia_chi": dia_chi,
            "so_don_hang": so_don_hang,
            "tong_chi_tieu": tong_chi_tieu,
        })

    return render(request, "QuanLyKhachHang/QuanLyKhachHang.html", {
        "khach_hangs": khach_hangs
    })