from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import json
from django.db.models import Q
from django.db.models.functions import Lower
import unicodedata
from quanLySanPham.models import DanhMuc
from quanLySanPham.models import SanPham, BienTheSanPham
from quanLyKhachHang.models import KhachHang, ChiTietKhachHang
from QuanLyKhuyenMai.models import KhuyenMai, SanPham_KhuyenMai
from .models import GioHang, ChiTietGioHang
from donDat.models import DonDat
import requests
from django.http import JsonResponse

def tao_ma_khach_hang():
    # Không còn dùng để tự tạo tự động do gây đụng độ với user.id
    pass


def tao_ma_gio_hang():
    so = GioHang.objects.count() + 1
    ma = f"GH{so:07d}"
    while GioHang.objects.filter(GH_Ma=ma).exists():
        so += 1
        ma = f"GH{so:07d}"
    return ma


def lay_hoac_tao_khach_hang(request):
    if request.user.is_authenticated:
        kh_ma = f"KH{request.user.id:07d}"
        kh, created = KhachHang.objects.get_or_create(
            KH_Ma=kh_ma,
            defaults={'KH_Ten': request.user.first_name + " " + request.user.last_name if (request.user.first_name or request.user.last_name) else request.user.username}
        )
        # Sửa lỗi: nếu trước đó bị đè Khach le, cập nhật lại tên
        if kh.KH_Ten == 'Khach le':
            kh.KH_Ten = request.user.first_name + " " + request.user.last_name if (request.user.first_name or request.user.last_name) else request.user.username
            kh.save()
        return kh
        
    kh, created = KhachHang.objects.get_or_create(
        KH_Ma='KH0000000',
        defaults={
            'KH_Ten': 'Khach le',
            'KH_TongChiTieu': 0,
            'KH_SoDonHang': 0
        }
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

    danh_muc_nam = DanhMuc.objects.filter(DM_Thuoc='NAM').order_by('DM_Ten')
    danh_muc_nu = DanhMuc.objects.filter(DM_Thuoc='NỮ').order_by('DM_Ten')

    return render(request, 'gioHang/trangChuUser.html', {
        'san_phams': san_phams,
        'danh_muc_nam': danh_muc_nam,
        'danh_muc_nu': danh_muc_nu,
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

    danh_muc_nam = DanhMuc.objects.filter(DM_Thuoc='NAM').order_by('DM_Ten')
    danh_muc_nu = DanhMuc.objects.filter(DM_Thuoc='NỮ').order_by('DM_Ten')

    return render(request, 'gioHang/chiTietSanPham.html', {
        'san_pham': san_pham,
        'bien_thes': bien_thes,
        'mau_sacs': mau_sacs,
        'kich_thuocs': kich_thuocs,
        'ton_kho_map': ton_kho_map,
        'danh_muc_nam': danh_muc_nam,
        'danh_muc_nu': danh_muc_nu,
    })


@login_required
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

    if bien_the.SP_SL <= 0:
        messages.error(request, 'Sản phẩm này đã hết hàng.')
        return redirect('chiTietSanPham', sp_ma=sp_ma)

    chi_tiet = ChiTietGioHang.objects.filter(
        GH_Ma=gio_hang,
        BTSP_Ma=bien_the
    ).first()

    if chi_tiet:
        if chi_tiet.GH_SL + so_luong > bien_the.SP_SL:
            messages.error(request, f'Số lượng vượt quá tồn kho (chỉ còn {bien_the.SP_SL}).')
            return redirect('chiTietSanPham', sp_ma=sp_ma)
        chi_tiet.GH_SL += so_luong
        chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * san_pham.SP_GiaBan
        chi_tiet.save()
    else:
        if so_luong > bien_the.SP_SL:
            messages.error(request, f'Số lượng vượt quá tồn kho (chỉ còn {bien_the.SP_SL}).')
            return redirect('chiTietSanPham', sp_ma=sp_ma)
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
    gio_hang = lay_hoac_tao_gio_hang(request)
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related(
        'BTSP_Ma', 'BTSP_Ma__SP_Ma'
    )
    cap_nhat_tong_gio_hang(gio_hang)

    danh_muc_nam = DanhMuc.objects.filter(DM_Thuoc='NAM').order_by('DM_Ten')
    danh_muc_nu = DanhMuc.objects.filter(DM_Thuoc='NỮ').order_by('DM_Ten')

    return render(request, 'gioHang/gio_hang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'danh_muc_nam': danh_muc_nam,
        'danh_muc_nu': danh_muc_nu,
    })


@login_required
def xoa_san_pham_khoi_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang(request)
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)
    chi_tiet.delete()
    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


@login_required
def xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang(request)
    ChiTietGioHang.objects.filter(GH_Ma=gio_hang).delete()
    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


@login_required
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

    if bien_the_moi.SP_SL <= 0:
        messages.error(request, 'Sản phẩm này đã hết hàng.')
        return redirect('gioHang')

    dong_da_co = ChiTietGioHang.objects.filter(
        GH_Ma=gio_hang,
        BTSP_Ma=bien_the_moi
    ).exclude(id=chi_tiet.id).first()

    if dong_da_co:
        if dong_da_co.GH_SL + so_luong > bien_the_moi.SP_SL:
            messages.error(request, f'Số lượng vượt quá tồn kho (chỉ còn {bien_the_moi.SP_SL}).')
            return redirect('gioHang')
        dong_da_co.GH_SL += so_luong
        dong_da_co.GH_TTien = Decimal(dong_da_co.GH_SL) * sp.SP_GiaBan
        dong_da_co.save()
        chi_tiet.delete()
    else:
        if so_luong > bien_the_moi.SP_SL:
            messages.error(request, f'Số lượng vượt quá tồn kho (chỉ còn {bien_the_moi.SP_SL}).')
            return redirect('gioHang')
        chi_tiet.BTSP_Ma = bien_the_moi
        chi_tiet.GH_SL = so_luong
        chi_tiet.GH_TTien = Decimal(so_luong) * sp.SP_GiaBan
        chi_tiet.save()

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')

@login_required
def xac_nhan_xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang(request)
    ds_chi_tiet = ChiTietGioHang.objects.filter(GH_Ma=gio_hang).select_related('BTSP_Ma', 'BTSP_Ma__SP_Ma')
    cap_nhat_tong_gio_hang(gio_hang)

    danh_muc_nam = DanhMuc.objects.filter(DM_Thuoc='NAM').order_by('DM_Ten')
    danh_muc_nu = DanhMuc.objects.filter(DM_Thuoc='NỮ').order_by('DM_Ten')

    return render(request, 'gioHang/XoaGioHang.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
        'danh_muc_nam': danh_muc_nam,
        'danh_muc_nu': danh_muc_nu,
    })


@login_required
def xoa_gio_hang(request):
    gio_hang = lay_hoac_tao_gio_hang(request)

    if request.method == 'POST':
        ChiTietGioHang.objects.filter(GH_Ma=gio_hang).delete()
        cap_nhat_tong_gio_hang(gio_hang)

    return redirect('gioHang')

@login_required
def tang_so_luong_gio(request, ctgh_id):
    gio_hang = lay_hoac_tao_gio_hang(request)
    chi_tiet = get_object_or_404(ChiTietGioHang, id=ctgh_id, GH_Ma=gio_hang)

    if chi_tiet.GH_SL + 1 > chi_tiet.BTSP_Ma.SP_SL:
        messages.error(request, f'Số lượng vượt quá tồn kho (chỉ còn {chi_tiet.BTSP_Ma.SP_SL}).')
        return redirect('gioHang')

    chi_tiet.GH_SL += 1
    chi_tiet.GH_TTien = Decimal(chi_tiet.GH_SL) * chi_tiet.BTSP_Ma.SP_Ma.SP_GiaBan
    chi_tiet.save()

    cap_nhat_tong_gio_hang(gio_hang)
    return redirect('gioHang')


@login_required
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


@login_required
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
            # Luôn tìm kiếm xem đã có địa chỉ/thông tin nào giống y hệt chưa
            ctkh = ChiTietKhachHang.objects.filter(
                KH_Ma=kh,
                CTKH_HoTenNguoiNhan=ho_ten,
                CTKH_SDT=so_dien_thoai,
                CTKH_DiaChi=dia_chi
            ).first()

            if not ctkh:
                # Nếu chưa có, tạo mới 1 CTKH để lưu lịch sử (không ghi đè để tránh hỏng đơn hàng cũ)
                so_ctkh = ChiTietKhachHang.objects.count() + 1
                ctkh_ma = f"CTKH{so_ctkh:05d}"
                
                # Đảm bảo mã không bị trùng
                while ChiTietKhachHang.objects.filter(CTKH_Ma=ctkh_ma).exists():
                    so_ctkh += 1
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
            while DonDat.objects.filter(TT_Ma=tt_ma).exists():
                so_don += 1
                tt_ma = f"DD{so_don:07d}"

            phuong_thuc = "Thanh toán khi nhận hàng (COD)" if payment == "COD" else "Chuyển khoản qua ngân hàng"
            
            expected_delivery_date = request.POST.get('expected_delivery_date')

            DonDat.objects.create(
                TT_Ma=tt_ma,
                GH_Ma=gio_hang,
                CTKH_Ma=ctkh,
                TT_TongPhiVC=phi_van_chuyen,
                TT_TongThanhToan=tong_thanh_toan,
                TT_PhuongThuc=phuong_thuc,
                TT_TongTienHang=tong_tien_hang,
                TT_NgayThanhToan=None,
                TT_NgayGiaoDuKien=expected_delivery_date if expected_delivery_date else None
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

            if payment == 'COD':
                messages.success(request, 'Đặt hàng thành công! Vui lòng thanh toán khi nhận hàng.')
            else:
                messages.success(request, 'Thanh toán thành công!')
            return redirect('quanLyDonDat')

    danh_muc_nam = DanhMuc.objects.filter(DM_Thuoc='NAM').order_by('DM_Ten')
    danh_muc_nu = DanhMuc.objects.filter(DM_Thuoc='NỮ').order_by('DM_Ten')

    return render(request, 'gioHang/ThanhToan.html', {
        'gio_hang_obj': gio_hang,
        'ds_chi_tiet': ds_chi_tiet,
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
        'danh_muc_nam': danh_muc_nam,
        'danh_muc_nu': danh_muc_nu,
    })


def normalize_text(text):
    if not text:
        return ''
    text = str(text).strip().lower()
    text = unicodedata.normalize('NFC', text)
    return ' '.join(text.split())


def danhSachSanPham(request):
    ds_san_pham = SanPham.objects.filter(SP_TrangThai=0).select_related('DM_Ma').order_by('SP_Ten')

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

            if all(tu in noi_dung_tim for tu in tu_khoa_list):
                ket_qua.append(sp)

        ds_san_pham = ket_qua

    else:
        if gioi_tinh:
            ds_san_pham = ds_san_pham.filter(DM_Ma__DM_Thuoc__iexact=gioi_tinh)

        if danh_muc:
            ds_san_pham = ds_san_pham.filter(DM_Ma__DM_Ten__iexact=danh_muc)

    danh_muc_nam = DanhMuc.objects.filter(DM_Thuoc='NAM').order_by('DM_Ten')
    danh_muc_nu = DanhMuc.objects.filter(DM_Thuoc='NỮ').order_by('DM_Ten')

    return render(request, 'sanpham/danh_sach_san_pham.html', {
        'ds_san_pham': ds_san_pham,
        'gioi_tinh_da_chon': gioi_tinh,
        'danh_muc_da_chon': danh_muc,
        'tu_khoa': q,
        'danh_muc_nam': danh_muc_nam,
        'danh_muc_nu': danh_muc_nu,
    })

def get_shipping_info(request):
    address_str = request.GET.get('address', '')
    
    # Thông tin shop
    GHN_TOKEN = "dc8f38d8-4509-11f1-bc69-ee9455d43f1a"
    SHOP_ID = "6412169"
    
    # Kho hàng tại Đà Nẵng
    FROM_DISTRICT_ID = 1454 
    FROM_WARD_CODE = "21211"

    headers = {
        "Token": GHN_TOKEN,
        "ShopId": SHOP_ID,
        "Content-Type": "application/json"
    }

    try:
        # TÌM DISTRICT_ID TỪ ĐỊA CHỈ PHONTON
        district_url = "https://online-gateway.ghn.vn/shiip/public-api/master-data/district"
        res_district = requests.get(district_url, headers=headers).json()
        
        if res_district.get('code') != 200:
            error_msg = res_district.get('message', 'Không thể kết nối GHN')
            return JsonResponse({'error': f'Lỗi GHN: {error_msg}'}, status=400)

        districts = res_district.get('data') or []
        
        import re
        target_district_id = None
        addr_lower = address_str.lower()
        for d in districts:
            d_name = d.get('DistrictName', '')
            if not d_name:
                continue
            # Xóa các tiền tố phổ biến của GHN để so khớp tốt hơn với Photon API (vd: "Huyện Hải Lăng" -> "Hải Lăng")
            clean_name = re.sub(r'^(Huyện|Quận|Thành phố|Thị xã|Tỉnh)\s+', '', d_name, flags=re.IGNORECASE)
            
            if clean_name.lower() in addr_lower:
                target_district_id = d.get('DistrictID')
                break
        
        if not target_district_id:
            return JsonResponse({'error': 'Không tìm thấy Quận/Huyện hợp lệ trong địa chỉ này.'}, status=400)

        # TÌM WARD_CODE
        ward_url = f"https://online-gateway.ghn.vn/shiip/public-api/master-data/ward?district_id={target_district_id}"
        res_ward = requests.get(ward_url, headers=headers).json()
        wards = res_ward.get('data') or []
        
        target_ward_code = None
        for w in wards:
            w_name = w.get('WardName', '')
            if not w_name: continue
            clean_w_name = re.sub(r'^(Phường|Xã|Thị trấn)\s+', '', w_name, flags=re.IGNORECASE)
            if clean_w_name.lower() in addr_lower:
                target_ward_code = w.get('WardCode')
                break
                
        # Nếu không tìm thấy chính xác, lấy phường/xã đầu tiên làm ước lượng thời gian
        if not target_ward_code and len(wards) > 0:
            target_ward_code = wards[0].get('WardCode')
            
        if not target_ward_code:
            return JsonResponse({'error': 'Không tìm thấy dữ liệu Phường/Xã cho Quận/Huyện này.'}, status=400)

        # TÍNH THỜI GIAN GIAO HÀNG (LEADTIME)
        leadtime_url = "https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/leadtime"
        payload = {
            "from_district_id": FROM_DISTRICT_ID,
            "from_ward_code": FROM_WARD_CODE,
            "to_district_id": target_district_id,
            "to_ward_code": target_ward_code,
            "service_id": 53320  # Dịch vụ Chuyển phát chuẩn
        }
        
        response = requests.post(leadtime_url, json=payload, headers=headers).json()

        
        if response.get('code') == 200:
            return JsonResponse({
                'status': 'success',
                'expected_timestamp': response['data']['leadtime']
            })
        else:
            err_msg = response.get('message', 'Lỗi không xác định từ GHN.')
            return JsonResponse({'error': f'GHN: {err_msg}'}, status=400)

    except Exception as e:
        return JsonResponse({'error': 'Lỗi kết nối máy chủ vận chuyển.'}, status=500)

