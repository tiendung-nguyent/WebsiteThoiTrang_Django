from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from .models import KhuyenMai, SanPham_KhuyenMai
from quanLySanPham.models import SanPham


def quan_ly_khuyen_mai_view(request):
    query = request.GET.get('q', '').strip()
    khuyenmais = KhuyenMai.objects.all()

    if query:
        khuyenmais = khuyenmais.filter(
            Q(KM_Ten__icontains=query) | Q(KM_Ma__icontains=query)
        )

    if query and not khuyenmais.exists():
        messages.error(request, 'Không tìm thấy khuyến mãi phù hợp')

    # Enrich with applied products
    km_data = []
    for km in khuyenmais:
        sps = SanPham_KhuyenMai.objects.filter(KM_Ma=km)
        sp_names = ", ".join([sp_km.SP_Ma.SP_Ten for sp_km in sps]) if sps else "Không có"
        km_data.append({
            'obj': km,
            'sp_names': sp_names,
            'sp_ma': sps.first().SP_Ma.SP_Ma if sps else ''
        })

    san_phams = SanPham.objects.all()
    context = {
        'khuyenmais': km_data,
        'search_query': query,
        'san_phams': san_phams,
    }
    return render(request, 'QuanLyKhuyenMai/QuanLyKhuyenMai.html', context)


def them_khuyen_mai_view(request):
    if request.method == 'POST':
        ten = request.POST.get('ten', '').strip()
        loai_giam = request.POST.get('loai_giam', '').strip()
        gia_tri = request.POST.get('gia_tri', '').strip()
        sp_ma = request.POST.get('sp_ma', '').strip()
        ngay_bd = request.POST.get('ngay_bd', '').strip()
        ngay_kt = request.POST.get('ngay_kt', '').strip()

        if not ten:
            messages.error(request, 'Tên khuyến mãi không hợp lệ, vui lòng nhập lại.')
            return redirect('quan_ly_khuyen_mai')
        if not loai_giam:
            messages.error(request, 'Tên loại giảm giá không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')
        if not gia_tri:
            messages.error(request, 'giá trị giảm không hợp lệ, vui lòng nhập lại')
            return redirect('quan_ly_khuyen_mai')
        if not sp_ma:
            messages.error(request, 'sản phẩm áp dụng không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')
        if not ngay_bd:
            messages.error(request, 'Ngày bắt đầu không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')
        if not ngay_kt:
            messages.error(request, 'Ngày kết thúc không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')

        try:
            d_bd = datetime.strptime(ngay_bd, '%Y-%m-%d').date()
            d_kt = datetime.strptime(ngay_kt, '%Y-%m-%d').date()
            if d_bd > d_kt:
                messages.error(request, 'Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc, vui lòng nhập lại.')
                return redirect('quan_ly_khuyen_mai')

            last_km = KhuyenMai.objects.order_by('KM_Ma').last()
            if last_km and last_km.KM_Ma.startswith('KM'):
                try:
                    num = int(last_km.KM_Ma[2:])
                    new_ma = f'KM{num + 1:03d}'
                except:
                    new_ma = f'KM{KhuyenMai.objects.count() + 1:03d}'
            else:
                new_ma = 'KM001'

            km = KhuyenMai.objects.create(
                KM_Ma=new_ma,
                KM_Ten=ten,
                KM_Loai=loai_giam,
                KM_GiaTri=gia_tri,
                KM_NgayBD=ngay_bd,
                KM_NgayKT=ngay_kt
            )

            sp = SanPham.objects.get(SP_Ma=sp_ma)
            SanPham_KhuyenMai.objects.create(KM_Ma=km, SP_Ma=sp)

            messages.success(request, 'Thêm khuyến mãi thành công')
        except Exception as e:
            messages.error(request, 'Không thể lưu, vui lòng thử lại sau.')

    return redirect('quan_ly_khuyen_mai')


def sua_khuyen_mai_view(request, ma_km):
    if request.method == 'POST':
        ten = request.POST.get('ten', '').strip()
        loai_giam = request.POST.get('loai_giam', '').strip()
        gia_tri = request.POST.get('gia_tri', '').strip()
        sp_ma = request.POST.get('sp_ma', '').strip()
        ngay_bd = request.POST.get('ngay_bd', '').strip()
        ngay_kt = request.POST.get('ngay_kt', '').strip()

        if not ten:
            messages.error(request, 'Tên khuyến mãi không hợp lệ, vui lòng nhập lại.')
            return redirect('quan_ly_khuyen_mai')
        if not loai_giam:
            messages.error(request, 'Tên loại giảm giá không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')
        if not gia_tri:
            messages.error(request, 'giá trị giảm không hợp lệ, vui lòng nhập lại')
            return redirect('quan_ly_khuyen_mai')
        if not sp_ma:
            messages.error(request, 'sản phẩm áp dụng không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')
        if not ngay_bd:
            messages.error(request, 'Ngày bắt đầu không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')
        if not ngay_kt:
            messages.error(request, 'Ngày kết thúc không hợp lệ, vui lòng chọn lại')
            return redirect('quan_ly_khuyen_mai')

        try:
            d_bd = datetime.strptime(ngay_bd, '%Y-%m-%d').date()
            d_kt = datetime.strptime(ngay_kt, '%Y-%m-%d').date()
            if d_bd > d_kt:
                messages.error(request, 'Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc, vui lòng nhập lại.')
                return redirect('quan_ly_khuyen_mai')

            km = get_object_or_404(KhuyenMai, KM_Ma=ma_km)
            km.KM_Ten = ten
            km.KM_Loai = loai_giam
            km.KM_GiaTri = gia_tri
            km.KM_NgayBD = d_bd
            km.KM_NgayKT = d_kt
            km.save()

            sp = SanPham.objects.get(SP_Ma=sp_ma)
            SanPham_KhuyenMai.objects.filter(KM_Ma=km).delete()
            SanPham_KhuyenMai.objects.create(KM_Ma=km, SP_Ma=sp)

            messages.success(request, 'Chỉnh sửa khuyến mãi thành công')
        except Exception as e:
            messages.error(request, 'Không thể cập nhật, vui lòng thử lại sau.')

    return redirect('quan_ly_khuyen_mai')


def xoa_khuyen_mai_view(request, ma_km):
    if request.method == 'POST':
        try:
            km = get_object_or_404(KhuyenMai, KM_Ma=ma_km)
            km.delete()
            messages.success(request, 'Xóa khuyến mãi thành công')
        except Exception as e:
            messages.error(request, 'Xóa khuyến mãi thất bại, vui lòng thử lại sau')

    return redirect('quan_ly_khuyen_mai')
