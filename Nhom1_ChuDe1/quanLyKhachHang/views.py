from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import KhachHang, ChiTietKhachHang
from donDat.models import DonDat
import json

def khach_hang_view(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            kh_ma = request.POST.get("KH_Ma")
            khach_hang = get_object_or_404(KhachHang, KH_Ma=kh_ma)
            khach_hang.delete()
            messages.success(request, "Xóa khách hàng thành công.")
            return redirect("quanLyKH")

    khach_hangs = []
    
    khach_hang_list = KhachHang.objects.all()
    for kh in khach_hang_list:
        don_hangs = DonDat.objects.filter(CTKH_Ma__KH_Ma=kh)
        
        # Nếu DB chưa cập nhật tự động KH_TongChiTieu, tính toán động từ DonDat
        calculated_so_don_hang = don_hangs.count()
        calculated_tong_chi_tieu = don_hangs.aggregate(tong=Sum("TT_TongThanhToan"))["tong"] or 0
        
        # Dùng dữ liệu của KhachHang nếu > 0, ngược lại dùng dữ liệu tính toán
        final_so_don_hang = kh.KH_SoDonHang if kh.KH_SoDonHang > 0 else calculated_so_don_hang
        final_tong_chi_tieu = kh.KH_TongChiTieu if kh.KH_TongChiTieu > 0 else calculated_tong_chi_tieu
        tong_chi_tieu_format = "{:,.0f}".format(final_tong_chi_tieu).replace(",", ".")

        # Lấy danh sách toàn bộ ChiTietKhachHang của KhachHang này
        chi_tiet_list = ChiTietKhachHang.objects.filter(KH_Ma=kh)
        ctkh_data = []
        for ct in chi_tiet_list:
            ctkh_data.append({
                "CTKH_Ma": ct.CTKH_Ma,
                "CTKH_HoTenNguoiNhan": ct.CTKH_HoTenNguoiNhan if ct.CTKH_HoTenNguoiNhan else "Chưa có",
                "CTKH_SDT": ct.CTKH_SDT if ct.CTKH_SDT else "Chưa có",
                "CTKH_DiaChi": ct.CTKH_DiaChi if ct.CTKH_DiaChi else "Chưa có",
            })
            
        # Lấy SĐT đại diện (từ đơn hàng mới nhất) để phục vụ việc search ngoài Grid
        latest_don_dat = don_hangs.order_by('-TT_NgayDatHang').first()
        if latest_don_dat and latest_don_dat.CTKH_Ma.CTKH_SDT:
            sdt_dai_dien = latest_don_dat.CTKH_Ma.CTKH_SDT
        else:
            sdt_dai_dien = chi_tiet_list.first().CTKH_SDT if chi_tiet_list.exists() else ""
        
        khach_hangs.append({
            "KH_Ma": kh.KH_Ma,
            "KH_Ten": kh.KH_Ten,
            "KH_SoDonHang": final_so_don_hang,
            "KH_TongChiTieu": tong_chi_tieu_format,
            "CTKH_SDT_DaiDien": sdt_dai_dien,
            "CTKH_List_JSON": json.dumps(ctkh_data)
        })

    return render(request, "QuanLyKhachHang/QuanLyKhachHang.html", {
        "khach_hangs": khach_hangs
    })