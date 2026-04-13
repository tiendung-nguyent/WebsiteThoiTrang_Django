from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from quanLySanPham.models import SanPham, BienTheSanPham
from quanLyKhachHang.models import KhachHang
from .models import GioHang, ChiTietGioHang


def tao_ma_khach_hang():
    so = KhachHang.objects.count() + 1
    return f"KH{so:07d}"


def tao_ma_gio_hang():
    so = GioHang.objects.count() + 1
    return f"GH{so:07d}"


def lay_hoac_tao_khach_hang_mac_dinh():
    kh = KhachHang.objects.first()

    if not kh:
        kh = KhachHang.objects.create(
            KH_Ma=tao_ma_khach_hang(),
            KH_Ten='Khach le',
            KH_TongChiTieu=0,
            KH_SoDonHang=0
        )

    return kh


def lay_hoac_tao_gio_hang():
    kh = lay_hoac_tao_khach_hang_mac_dinh()
    gio_hang = GioHang.objects.filter(KH_Ma=kh).first()

    if not gio_hang:
        gio_hang = GioHang.objects.create(
            GH_Ma=tao_ma_gio_hang(),
            KH_Ma=kh,
            GH_TongSL=0,
            GH_TamTinh=0
        )
    return gio_hang


def cap_nhat_tong_gio_hang(gio_hang):
    ds = ChiTietGioHang.objects.filter(GH_Ma=gio_hang)
    gio_hang.GH_TongSL = sum(item.GH_SL for item in ds)
    gio_hang.GH_TamTinh = sum(item.GH_TTien for item in ds)
    gio_hang.save()


def trangChuUser(request):
    san_phams = SanPham.objects.filter(SP_TrangThai=0).select_related('DM_Ma').order_by('SP_Ten')

    gio_hang = lay_hoac_tao_gio_hang()
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/trangChuUser.html', {
        'san_phams': san_phams,
        'cart_count': gio_hang.GH_TongSL,
    })


def chiTietSanPham(request, sp_ma):
    san_pham = get_object_or_404(SanPham, SP_Ma=sp_ma, SP_TrangThai=0)

    bien_thes = BienTheSanPham.objects.filter(SP_Ma=san_pham)
    mau_sacs = bien_thes.values_list('SP_MauSac', flat=True).distinct()
    kich_thuocs = bien_thes.values_list('SP_KichThuoc', flat=True).distinct()

    ton_kho_map = {}
    for bt in bien_thes:
        key = f"{bt.SP_MauSac}-{bt.SP_KichThuoc}"
        ton_kho_map[key] = bt.SP_SL

    gio_hang = lay_hoac_tao_gio_hang()
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/chiTietSanPham.html', {
        'san_pham': san_pham,
        'bien_thes': bien_thes,
        'mau_sacs': mau_sacs,
        'kich_thuocs': kich_thuocs,
        'ton_kho_map': ton_kho_map,
        'cart_count': gio_hang.GH_TongSL,
    })


def them_vao_gio_hang(request, sp_ma):
    if request.method != 'POST':
        return redirect('chiTietSanPham', sp_ma=sp_ma)

    san_pham = get_object_or_404(SanPham, SP_Ma=sp_ma, SP_TrangThai=0)
    gio_hang = lay_hoac_tao_gio_hang()

    try:
        so_luong = int(request.POST.get('so_luong', 1))
    except ValueError:
        so_luong = 1

    if so_luong < 1:
        so_luong = 1

    chi_tiet = ChiTietGioHang.objects.filter(
        GH_Ma=gio_hang,
        SP_Ma=san_pham
    ).first()

    if chi_tiet:
        chi_tiet.GH_SL += so_luong
        chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * san_pham.SP_GiaBan
        chi_tiet.save()
    else:
        ChiTietGioHang.objects.create(
            GH_Ma=gio_hang,
            SP_Ma=san_pham,
            GH_SL=so_luong,
            GH_TTien=Decimal(so_luong) * san_pham.SP_GiaBan
        )

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('chiTietSanPham', sp_ma=sp_ma)


def gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang()
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related('SP_Ma')
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/gio_hang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'cart_count': gio_hang.GH_TongSL,
    })


def thanh_toan_view(request):
    gio_hang = lay_hoac_tao_gio_hang()
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/ThanhToan.html', {
        'gio_hang_obj': gio_hang,
        'cart_count': gio_hang.GH_TongSL,
    })