from django.shortcuts import render
from django.contrib.auth.models import User
from accounts.models import Profile
from donDat.models import DonDat
from django.db.models import Count, Sum


def khach_hang_view(request):

    users = User.objects.all()

    khach_hangs = []

    for user in users:
        profile = Profile.objects.filter(user=user).first()

        # lấy đơn hàng theo user (⚠️ bạn phải có field liên kết)
        don_hangs = DonDat.objects.filter(
            # ⚠️ sửa lại nếu bạn dùng field khác
            # ví dụ: user=user hoặc account=user
        )

        so_don = don_hangs.count()
        tong_tien = don_hangs.aggregate(tong=Sum('TT_TongThanhToan'))['tong'] or 0

        khach_hangs.append({
            "KH_Ma": f"KH{user.id:07d}",
            "ho_ten": user.username,
            "so_dien_thoai": profile.phone_number if profile else "",
            "dia_chi": getattr(profile, "address", "") if profile else "",
            "so_don_hang": so_don,
            "tong_chi_tieu": tong_tien
        })

    return render(request, "QuanLyKhachHang/QuanLyKhachHang.html", {
        "khach_hangs": khach_hangs
    })