from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
from django.db.models import Q
from django.db.models.functions import Lower
import unicodedata

from quanLySanPham.models import SanPham, BienTheSanPham
from quanLyKhachHang.models import KhachHang, ChiTietKhachHang
from QuanLyKhuyenMai.models import KhuyenMai, SanPham_KhuyenMai
from .models import GioHang, ChiTietGioHang
from donDat.models import DonDat

def tao_ma_khach_hang():
    so = KhachHang.objects.count() + 1
    return f"KH{so:07d}"


def tao_ma_gio_hang():
    so = GioHang.objects.count() + 1
    return f"GH{so:07d}"


def lay_hoac_tao_khach_hang(request):
    if request.user.is_authenticated:
        kh_ma = f"KH{request.user.id:07d}"
        kh, created = KhachHang.objects.get_or_create(
            KH_Ma=kh_ma,
            defaults={'KH_Ten': request.user.username}
        )
        return kh
        
    kh = KhachHang.objects.filter(KH_Ten='Khach le').first()
    if not kh:
        kh = KhachHang.objects.create(
            KH_Ma=tao_ma_khach_hang(),
            KH_Ten='Khach le',
            KH_TongChiTieu=0,
            KH_SoDonHang=0
        )
    return kh


def lay_hoac_tao_gio_hang(request):
    kh = lay_hoac_tao_khach_hang(request)
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
    gio_hang = lay_hoac_tao_gio_hang(request)
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/trangChuUser.html', {
        'san_phams': san_phams,
        'cart_count': gio_hang.GH_TongSL,
    })


def chiTietSanPham(request, sp_ma):
    san_pham = get_object_or_404(SanPham, SP_Ma=sp_ma, SP_TrangThai=0)

    viewed_products = request.session.get('viewed_products', [])
    current_product = [san_pham.SP_Ma, san_pham.SP_Ten]

    if current_product in viewed_products:
        viewed_products.remove(current_product)

    viewed_products.insert(0, current_product)

    request.session['viewed_products'] = viewed_products[:5]
    request.session.modified = True

    bien_thes = BienTheSanPham.objects.filter(SP_Ma=san_pham)
    mau_sacs = bien_thes.values_list('SP_MauSac', flat=True).distinct()
    kich_thuocs = bien_thes.values_list('SP_KichThuoc', flat=True).distinct()

    ton_kho_map = {}
    for bt in bien_thes:
        key = f"{bt.SP_MauSac}-{bt.SP_KichThuoc}"
        ton_kho_map[key] = bt.SP_SL

    gio_hang = lay_hoac_tao_gio_hang(request)
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
    gio_hang = lay_hoac_tao_gio_hang(request)

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


def gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang(request)
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related(
        'BTSP_Ma', 'BTSP_Ma__SP_Ma'
    )
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/gio_hang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'cart_count': gio_hang.GH_TongSL,
    })


def xoa_san_pham_khoi_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang(request)
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)
    chi_tiet.delete()
    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


def xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang(request)
    ChiTietGioHang.objects.filter(GH_Ma=gio_hang).delete()
    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


def cap_nhat_san_pham_gio(request, ctgh_id):
    if request.method != 'POST':
        return redirect('gioHang')

    gio_hang = lay_hoac_tao_gio_hang(request)
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
    gio_hang = lay_hoac_tao_gio_hang(request)
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related('BTSP_Ma', 'BTSP_Ma__SP_Ma')
    cap_nhat_tong_gio_hang(gio_hang)

    return render(request, 'gioHang/XoaGioHang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'cart_count': gio_hang.GH_TongSL,
    })


def xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang(request)

    if request.method == 'POST':
        ChiTietGioHang.objects.filter(GH_Ma=gio_hang).delete()
        cap_nhat_tong_gio_hang(gio_hang)

    return redirect('gioHang')

def tang_so_luong_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang(request)
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)

    chi_tiet.GH_SL += 1
    chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * chi_tiet.BTSP_Ma.SP_Ma.SP_GiaBan
    chi_tiet.save()

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


def giam_so_luong_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang(request)
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
    kh = lay_hoac_tao_khach_hang(request)
    gio_hang = lay_hoac_tao_gio_hang(request)
    cap_nhat_tong_gio_hang(gio_hang)
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related(
        'BTSP_Ma', 'BTSP_Ma__SP_Ma'
    )

    if gio_hang.GH_TongSL == 0:
        messages.error(request, 'Giỏ hàng của bạn đang trống!')
        return redirect('gioHang')

    # Lấy danh sách địa chỉ đã lưu của khách hàng này
    ds_ctkh = ChiTietKhachHang.objects.filter(KH_Ma=kh)

    ho_ten = request.POST.get('ho_ten', '').strip() if request.method == 'POST' else ''
    so_dien_thoai = request.POST.get('so_dien_thoai', '').strip() if request.method == 'POST' else ''
    dia_chi = request.POST.get('dia_chi', '').strip() if request.method == 'POST' else ''
    ma_khuyen_mai = request.POST.get('ma_khuyen_mai', '') if request.method == 'POST' else ''
    payment = request.POST.get('payment', 'COD') if request.method == 'POST' else 'COD'
    ctkh_ma_selected = request.POST.get('ctkh_ma', '') if request.method == 'POST' else ''

    hom_nay = timezone.now().date()
    # Lấy các mã sản phẩm trong giỏ hàng
    sp_ids_trong_gio = [ct.BTSP_Ma.SP_Ma_id for ct in ds_chi_tiet]
    # Tìm các khuyến mãi có liên kết với sản phẩm trong giỏ
    km_hop_le_ids = SanPham_KhuyenMai.objects.filter(SP_Ma_id__in=sp_ids_trong_gio).values_list('KM_Ma_id', flat=True)

    khuyen_mais = KhuyenMai.objects.filter(
        KM_Ma__in=km_hop_le_ids,
        KM_NgayBD__lte=hom_nay,
        KM_NgayKT__gte=hom_nay
    ).distinct()

    giam_gia_dict = {}
    for km in khuyen_mais:
        sp_ap_dung_ids = SanPham_KhuyenMai.objects.filter(KM_Ma=km).values_list('SP_Ma_id', flat=True)
        tong_tien_sp_ap_dung = sum(ct.GH_TTien for ct in ds_chi_tiet if ct.BTSP_Ma.SP_Ma_id in sp_ap_dung_ids)

        giam_gia = km.KM_GiaTri
        loai = km.KM_Loai

        if loai == 'Phần trăm (%)':
            giam_gia_tien = tong_tien_sp_ap_dung * (giam_gia / Decimal('100'))
            display_val = f"{giam_gia:g}%"
        else:
            giam_gia_tien = giam_gia
            if giam_gia_tien > tong_tien_sp_ap_dung:
                giam_gia_tien = tong_tien_sp_ap_dung
            display_val = f"{giam_gia:,.0f} đ".replace(',', '.')

        giam_gia_dict[km.KM_Ma] = {
            'amount': float(giam_gia_tien),
            'display': display_val,
            'name': km.KM_Ten
        }

        # Tìm tên các sản phẩm trong giỏ hàng mà khuyến mãi này áp dụng
        sp_names = SanPham.objects.filter(
            SP_Ma__in=SanPham_KhuyenMai.objects.filter(KM_Ma=km).values_list('SP_Ma_id', flat=True)
        ).filter(SP_Ma__in=sp_ids_trong_gio).values_list('SP_Ten', flat=True)
        km.sp_ap_dung_names = ", ".join(sp_names)
        km.hien_thi_dropdown = f"Giảm {display_val} cho {km.sp_ap_dung_names}"

    giam_gia_json = json.dumps(giam_gia_dict)

    phi_van_chuyen = Decimal('30000')
    tong_tien_hang = gio_hang.GH_TamTinh
    tong_thanh_toan = tong_tien_hang + phi_van_chuyen

    khuyen_mai_obj = None
    hien_thi_giam_gia = "0 đ"

    if ma_khuyen_mai:
        khuyen_mai_obj = KhuyenMai.objects.filter(KM_Ma=ma_khuyen_mai).first()
        if khuyen_mai_obj:
            giam_gia = khuyen_mai_obj.KM_GiaTri
            loai = khuyen_mai_obj.KM_Loai

            sp_ap_dung_ids = SanPham_KhuyenMai.objects.filter(KM_Ma=khuyen_mai_obj).values_list('SP_Ma_id', flat=True)
            tong_tien_sp_ap_dung = sum(ct.GH_TTien for ct in ds_chi_tiet if ct.BTSP_Ma.SP_Ma_id in sp_ap_dung_ids)

            if loai == 'Phần trăm (%)':
                giam_gia_tien = tong_tien_sp_ap_dung * (giam_gia / Decimal('100'))
                hien_thi_giam_gia = f"{giam_gia:g}%"
            else:
                giam_gia_tien = giam_gia
                if giam_gia_tien > tong_tien_sp_ap_dung:
                    giam_gia_tien = tong_tien_sp_ap_dung
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
            if ctkh_ma_selected:
                ctkh = ChiTietKhachHang.objects.filter(CTKH_Ma=ctkh_ma_selected, KH_Ma=kh).first()
                if ctkh:
                    ctkh.CTKH_HoTenNguoiNhan = ho_ten
                    ctkh.CTKH_SDT = so_dien_thoai
                    ctkh.CTKH_DiaChi = dia_chi
                    ctkh.save()
                else:
                    so_ctkh = ChiTietKhachHang.objects.count() + 1
                    ctkh_ma = f"CTKH{so_ctkh:05d}"
                    ctkh = ChiTietKhachHang.objects.create(
                        CTKH_Ma=ctkh_ma,
                        KH_Ma=kh,
                        CTKH_HoTenNguoiNhan=ho_ten,
                        CTKH_SDT=so_dien_thoai,
                        CTKH_DiaChi=dia_chi
                    )
            else:
                so_ctkh = ChiTietKhachHang.objects.count() + 1
                ctkh_ma = f"CTKH{so_ctkh:05d}"
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

            cap_nhat_tong_gio_hang(gio_hang)
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
        'giam_gia_json': giam_gia_json,
        'ds_ctkh': ds_ctkh,
    })


def normalize_text(text):
    if not text:
        return ''
    text = str(text).strip().lower()
    text = unicodedata.normalize('NFC', text)
    return ' '.join(text.split())


def danhSachSanPham(request):
    ds_san_pham = SanPham.objects.select_related('DM_Ma').all()

    gioi_tinh = request.GET.get('gioi_tinh', '').strip()
    danh_muc = request.GET.get('danh_muc', '').strip()
    q = request.GET.get('q', '').strip()

    if q:
        q_normalized = normalize_text(q)
        tu_khoa_list = q_normalized.split()

        ket_qua = []

        for sp in ds_san_pham:
            ten_sp = normalize_text(sp.SP_Ten)
            mo_ta_sp = normalize_text(sp.SP_MoTa)
            noi_dung_tim = f"{ten_sp} {mo_ta_sp}"

            # tất cả từ trong ô search đều phải xuất hiện
            if all(tu in noi_dung_tim for tu in tu_khoa_list):
                ket_qua.append(sp)

        ds_san_pham = ket_qua

    else:
        if gioi_tinh:
            ds_san_pham = ds_san_pham.filter(DM_Ma__DM_Thuoc__iexact=gioi_tinh)

        if danh_muc:
            ds_san_pham = ds_san_pham.filter(DM_Ma__DM_Ten__iexact=danh_muc)

    return render(request, 'sanpham/danh_sach_san_pham.html', {
        'ds_san_pham': ds_san_pham,
        'gioi_tinh_da_chon': gioi_tinh,
        'danh_muc_da_chon': danh_muc,
        'tu_khoa': q,
    })