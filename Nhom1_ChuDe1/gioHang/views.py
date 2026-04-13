from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from quanLySanPham.models import SanPham, BienTheSanPham
from quanLyKhachHang.models import KhachHang, ChiTietKhachHang
from QuanLyKhuyenMai.models import KhuyenMai
from .models import GioHang, ChiTietGioHang
from donDat.models import DonDat

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
    # Tim gio hang chua thanh toan (chua co DonDat lien ket)
    gio_hang = GioHang.objects.filter(KH_Ma=kh, dondat__isnull=True).last()

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
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related(
        'BTSP_Ma', 'BTSP_Ma__SP_Ma'
    )

    if gio_hang.GH_TongSL == 0:
        messages.error(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('gioHang')

    ho_ten = request.POST.get('ho_ten', '').strip() if request.method == 'POST' else ''
    so_dien_thoai = request.POST.get('so_dien_thoai', '').strip() if request.method == 'POST' else ''
    dia_chi = request.POST.get('dia_chi', '').strip() if request.method == 'POST' else ''
    ma_khuyen_mai = request.POST.get('ma_khuyen_mai', '') if request.method == 'POST' else ''
    payment = request.POST.get('payment', 'COD') if request.method == 'POST' else 'COD'

    hom_nay = timezone.now().date()
    khuyen_mais = KhuyenMai.objects.filter(
        KM_NgayBD__lte=hom_nay,
        KM_NgayKT__gte=hom_nay
    )

    phi_van_chuyen = Decimal('30000')
    tong_tien_hang = gio_hang.GH_TamTinh
    tong_thanh_toan = tong_tien_hang + phi_van_chuyen

    khuyen_mai_obj = None
    hien_thi_giam_gia = "0 đ"

    if ma_khuyen_mai:
        khuyen_mai_obj = KhuyenMai.objects.filter(KM_Ma=ma_khuyen_mai).first()
        if khuyen_mai_obj:
            giam_gia = khuyen_mai_obj.KM_GiaTri
            if giam_gia < 100:
                giam_gia_tien = tong_tien_hang * (giam_gia / Decimal('100'))
                hien_thi_giam_gia = f"{giam_gia}%"
            else:
                giam_gia_tien = giam_gia
                hien_thi_giam_gia = f"{giam_gia:,.0f} đ".replace(',', '.')

            tong_thanh_toan -= giam_gia_tien
            if tong_thanh_toan < 0:
                tong_thanh_toan = Decimal('0')

    if request.method == 'POST':
        loi = None
        if not ho_ten:
            loi = 'Họ tên không được để trống, vui lòng nhập lại'
        elif not (len(so_dien_thoai) == 10 and so_dien_thoai.startswith('0')):
            loi = 'Số điện thoại không hợp lệ, vui lòng đặt lại'
        elif not dia_chi:
            loi = 'Địa chỉ không được để trống.'

        if loi:
            messages.error(request, loi)
        else:
            so_ctkh = ChiTietKhachHang.objects.count() + 1
            ctkh_ma = f"CTKH{so_ctkh:05d}"

            kh = lay_hoac_tao_khach_hang_mac_dinh()

            ctkh = ChiTietKhachHang.objects.create(
                CTKH_Ma=ctkh_ma,
                KH_Ma=kh,
                CTKH_HoTenNguoiNhan=ho_ten,
                CTKH_SDT=so_dien_thoai,
                CTKH_DiaChi=dia_chi
            )

            so_don = DonDat.objects.count() + 1
            tt_ma = f"DD{so_don:07d}"

            phuong_thuc = "Thanh toán khi nhận hàng (COD)" if payment == "COD" else "Chuyển khoản qua ngân hàng"

            DonDat.objects.create(
                TT_Ma=tt_ma,
                GH_Ma=gio_hang,
                CTKH_Ma=ctkh,
                TT_TongPhiVC=phi_van_chuyen,
                TT_TongThanhToan=tong_thanh_toan,
                TT_PhuongThuc=phuong_thuc,
                TT_TongTienHang=tong_tien_hang,
                TT_NgayThanhToan=None
            )

            kh.KH_TongChiTieu += tong_thanh_toan
            kh.KH_SoDonHang += 1
            kh.save()

            # Giữ nguyên chi tiết giỏ hàng của đơn vừa thanh toán
            cap_nhat_tong_gio_hang(gio_hang)

            # Tạo giỏ hàng mới cho lần mua tiếp theo
            GioHang.objects.create(
                GH_Ma=tao_ma_gio_hang(),
                KH_Ma=kh,
                GH_TongSL=0,
                GH_TamTinh=0
            )

            messages.success(request, 'Thanh toán thành công')
            return redirect('quanLyDonDat')

    return render(request, 'gioHang/ThanhToan.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'cart_count': gio_hang.GH_TongSL,
        'khuyen_mais': khuyen_mais,
        'phi_van_chuyen': phi_van_chuyen,
        'tong_thanh_toan': tong_thanh_toan,
        'ho_ten': ho_ten,
        'so_dien_thoai': so_dien_thoai,
        'dia_chi': dia_chi,
        'ma_khuyen_mai': ma_khuyen_mai,
        'khuyen_mai_obj': khuyen_mai_obj,
        'hien_thi_giam_gia': hien_thi_giam_gia,
        'payment': payment,
    })