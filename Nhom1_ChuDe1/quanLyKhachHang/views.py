from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import KhachHang, ChiTietKhachHang
from donDat.models import DonDat

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
        
        # Ưu tiên lấy chi tiết khách hàng từ đơn đặt hàng gần nhất (thông tin giỏ hàng/thanh toán)
        latest_don_dat = don_hangs.order_by('-TT_NgayDatHang').first()
        if latest_don_dat:
            chi_tiet = latest_don_dat.CTKH_Ma
        else:
            chi_tiet = ChiTietKhachHang.objects.filter(KH_Ma=kh).first()
            
        ho_ten_nguoi_nhan = chi_tiet.CTKH_HoTenNguoiNhan if chi_tiet else "Chưa có thông tin"
        sdt = chi_tiet.CTKH_SDT if chi_tiet else "Chưa có thông tin"
        dia_chi = chi_tiet.CTKH_DiaChi if chi_tiet else "Chưa có thông tin"
        
        # Nếu DB chưa cập nhật tự động KH_TongChiTieu, tính toán động từ DonDat
        calculated_so_don_hang = don_hangs.count()
        calculated_tong_chi_tieu = don_hangs.aggregate(tong=Sum("TT_TongThanhToan"))["tong"] or 0
        
        # Dùng dữ liệu của KhachHang nếu > 0, ngược lại dùng dữ liệu tính toán (để đảm bảo luôn có số liệu đúng)
        final_so_don_hang = kh.KH_SoDonHang if kh.KH_SoDonHang > 0 else calculated_so_don_hang
        final_tong_chi_tieu = kh.KH_TongChiTieu if kh.KH_TongChiTieu > 0 else calculated_tong_chi_tieu
        
        tong_chi_tieu_format = "{:,.0f}".format(final_tong_chi_tieu).replace(",", ".")
        
        khach_hangs.append({
            "KH_Ma": kh.KH_Ma,
            "KH_Ten": kh.KH_Ten,
            "CTKH_Ma": chi_tiet.CTKH_Ma if chi_tiet else "Chưa có thông tin",
            "CTKH_HoTenNguoiNhan": ho_ten_nguoi_nhan,
            "CTKH_SDT": sdt,
            "CTKH_DiaChi": dia_chi,
            "KH_SoDonHang": final_so_don_hang,
            "KH_TongChiTieu": tong_chi_tieu_format,
        })

    return render(request, "QuanLyKhachHang/QuanLyKhachHang.html", {
        "khach_hangs": khach_hangs
    })