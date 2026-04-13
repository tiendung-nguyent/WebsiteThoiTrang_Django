from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import DanhMuc


def tao_ma_danh_muc():
    danh_muc_cuoi = DanhMuc.objects.order_by('DM_Ma').last()
    if danh_muc_cuoi:
        so_cuoi = int(danh_muc_cuoi.DM_Ma[2:])
        so_moi = so_cuoi + 1
    else:
        so_moi = 1
    return f"DM{so_moi:03d}"


def danh_muc_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        # THÊM
        if action == "create":
            ten = request.POST.get("DM_Ten", "").strip()
            thuoc = request.POST.get("DM_Thuoc", "").strip()

            if not ten:
                messages.error(request, "Tên danh mục không được để trống.")
                return redirect("quanLyDM"
                                "")

            DanhMuc.objects.create(
                DM_Ma=tao_ma_danh_muc(),
                DM_Ten=ten,
                DM_Thuoc=thuoc
            )
            messages.success(request, "Thêm danh mục thành công.")
            return redirect("quanLyDM")

        # SỬA
        elif action == "update":
            ma = request.POST.get("DM_Ma")
            ten = request.POST.get("DM_Ten", "").strip()

            if not ten:
                messages.error(request, "Tên danh mục không được để trống.")
                return redirect("quanLyDM")

            danh_muc = get_object_or_404(DanhMuc, DM_Ma=ma)
            danh_muc.DM_Ten = ten
            danh_muc.save()

            messages.success(request, "Cập nhật danh mục thành công.")
            return redirect("quanLyDM")

        # XÓA
        elif action == "delete":
            ma = request.POST.get("DM_Ma")
            danh_muc = get_object_or_404(DanhMuc, DM_Ma=ma)
            danh_muc.delete()

            messages.success(request, "Xóa danh mục thành công.")
            return redirect("quanLyDM")

    danh_mucs = DanhMuc.objects.all().order_by("DM_Ma")

    context = {
        "danh_mucs": danh_mucs,
        "ma_danh_muc_moi": tao_ma_danh_muc(),
    }
    return render(request, "QuanLyDanhMuc/QuanLyDanhMuc.html", context)