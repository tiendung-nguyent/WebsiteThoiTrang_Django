from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

    mau_sac = request.POST.get('mau_sac')
    kich_thuoc = request.POST.get('kich_thuoc')

    try:
        so_luong = int(request.POST.get('so_luong', 1))
    except ValueError:
        so_luong = 1

    if so_luong < 1:
        so_luong = 1

    bien_the = None
    if mau_sac and kich_thuoc:
        bien_the = BienTheSanPham.objects.filter(
            SP_Ma=san_pham,
            SP_MauSac=mau_sac,
            SP_KichThuoc=kich_thuoc
        ).first()
    else:
        bien_the = BienTheSanPham.objects.filter(SP_Ma=san_pham).first()

    if not bien_the:
        messages.error(request, 'Không tìm thấy biến thể sản phẩm.')
        return redirect('chiTietSanPham', sp_ma=sp_ma)

    chi_tiet = ChiTietGioHang.objects.filter(
        GH_Ma=gio_hang,
        BTSP_Ma=bien_the
    ).first()

    if chi_tiet:
        chi_tiet.GH_SL += so_luong
        chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * san_pham.SP_GiaBan
        chi_tiet.save()
    else:
        ChiTietGioHang.objects.create(
            GH_Ma=gio_hang,
            BTSP_Ma=bien_the,
            GH_SL=so_luong,
            GH_TTien=Decimal(so_luong) * san_pham.SP_GiaBan
        )

    cap_nhat_tong_gio_hang(gio_hang)
    messages.success(request, 'Đã thêm sản phẩm vào giỏ hàng.')
    return redirect('chiTietSanPham', sp_ma=sp_ma)


@login_required
def gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang()
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related(
        'BTSP_Ma', 'BTSP_Ma__SP_Ma'
    )
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/gio_hang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'cart_count': gio_hang.GH_TongSL,
    })


@login_required
def xoa_san_pham_khoi_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang()
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)
    chi_tiet.delete()
    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


def xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang()
    ChiTietGioHang.objects.filter(GH_Ma=gio_hang).delete()
    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


def cap_nhat_san_pham_gio(request, ctgh_id):
    if request.method != 'POST':
        return redirect('gioHang')

    gio_hang = lay_hoac_tao_gio_hang()
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)

    mau_sac = request.POST.get('mau_sac')
    kich_thuoc = request.POST.get('kich_thuoc')

    try:
        so_luong = int(request.POST.get('so_luong', 1))
    except ValueError:
        so_luong = 1

    if so_luong < 1:
        so_luong = 1

    sp = chi_tiet.BTSP_Ma.SP_Ma

    bien_the_moi = BienTheSanPham.objects.filter(
        SP_Ma=sp,
        SP_MauSac=mau_sac,
        SP_KichThuoc=kich_thuoc
    ).first()

    if not bien_the_moi:
        messages.error(request, 'Biến thể không hợp lệ.')
        return redirect('gioHang')

    dong_da_co = ChiTietGioHang.objects.filter(
        GH_Ma=gio_hang,
        BTSP_Ma=bien_the_moi
    ).exclude(id=chi_tiet.id).first()

    if dong_da_co:
        dong_da_co.GH_SL += so_luong
        dong_da_co.GH_TTien = Decimal(dong_da_co.GH_SL) * sp.SP_GiaBan
        dong_da_co.save()
        chi_tiet.delete()
    else:
        chi_tiet.BTSP_Ma = bien_the_moi
        chi_tiet.GH_SL = so_luong
        chi_tiet.GH_TTien = Decimal(so_luong) * sp.SP_GiaBan
        chi_tiet.save()

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')

def xac_nhan_xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang()
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related(
        'BTSP_Ma', 'BTSP_Ma__SP_Ma'
    )
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/XoaGioHang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'cart_count': gio_hang.GH_TongSL,
    })


def xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang()

    if request.method == 'POST':
        ChiTietGioHang.objects.filter(GH_Ma=gio_hang).delete()
        cap_nhat_tong_gio_hang(gio_hang)

    return redirect('gioHang')
def tang_so_luong_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang()
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)

    chi_tiet.GH_SL += 1
    chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * chi_tiet.BTSP_Ma.SP_Ma.SP_GiaBan
    chi_tiet.save()

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


def giam_so_luong_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang()
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)

    if chi_tiet.GH_SL > 1:
        chi_tiet.GH_SL -= 1
        chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * chi_tiet.BTSP_Ma.SP_Ma.SP_GiaBan
        chi_tiet.save()
    else:
        chi_tiet.delete()

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')
def thanh_toan_view(request):
    gio_hang = lay_hoac_tao_gio_hang()
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/ThanhToan.html', {
        'gio_hang_obj': gio_hang,
        'cart_count': gio_hang.GH_TongSL,
    })