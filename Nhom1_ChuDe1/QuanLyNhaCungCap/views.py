from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import NhaCungCap


def quan_ly_ncc_view(request):
    query = request.GET.get('q', '').strip()
    nhacungcaps = NhaCungCap.objects.all()

    if query:
        nhacungcaps = nhacungcaps.filter(
            Q(NCC_Ma__icontains=query) | Q(NCC_Ten__icontains=query)
        )

    context = {
        'nhacungcaps': nhacungcaps,
        'search_query': query,
    }
    return render(request, 'QuanLyNhaCungCap/QuanLyNhaCungCap.html', context)


def them_ncc_view(request):
    if request.method == 'POST':
        ten = request.POST.get('ten', '').strip()
        sdt = request.POST.get('sdt', '').strip()
        dchi = request.POST.get('dchi', '').strip()

        if not ten:
            messages.error(request, 'Tên nhà cung cấp không hợp lệ, vui lòng nhập lại.')
            return redirect('quan_ly_ncc')
        if not dchi:
            messages.error(request, 'Tên địa chỉ không hợp lệ, vui lòng nhập lại.')
            return redirect('quan_ly_ncc')
        if not sdt or len(sdt) != 10 or not sdt.startswith('0') or not sdt.isdigit():
            messages.error(request, 'số điện thoại không hợp lệ, vui lòng đặt lại.')  # matched requirement note: 5a
            return redirect('quan_ly_ncc')

        last_ncc = NhaCungCap.objects.order_by('NCC_Ma').last()
        if last_ncc and last_ncc.NCC_Ma.startswith('NCC'):
            try:
                num = int(last_ncc.NCC_Ma[3:])
                new_ma = f'NCC{num + 1:03d}'
            except:
                new_ma = f'NCC{NhaCungCap.objects.count() + 1:03d}'
        else:
            new_ma = 'NCC001'

        try:
            NhaCungCap.objects.create(NCC_Ma=new_ma, NCC_Ten=ten, NCC_SDT=sdt, NCC_DChi=dchi)
            messages.success(request, 'Thêm nhà cung cấp thành công')
        except Exception as e:
            messages.error(request, 'Không thể lưu, vui lòng thử lại sau.')

    return redirect('quan_ly_ncc')


def sua_ncc_view(request, ma_ncc):
    if request.method == 'POST':
        ten = request.POST.get('ten', '').strip()
        sdt = request.POST.get('sdt', '').strip()
        dchi = request.POST.get('dchi', '').strip()

        if not ten:
            messages.error(request, 'Tên nhà cung cấp không hợp lệ, vui lòng đặt lại.')
            return redirect('quan_ly_ncc')
        if not dchi:
            messages.error(request, 'Tên địa chỉ không hợp lệ, vui lòng đặt lại.')
            return redirect('quan_ly_ncc')
        if not sdt or len(sdt) != 10 or not sdt.startswith('0') or not sdt.isdigit():
            messages.error(request, 'số điện thoại không hợp lệ, vui lòng đặt lại.')
            return redirect('quan_ly_ncc')

        try:
            ncc = get_object_or_404(NhaCungCap, NCC_Ma=ma_ncc)
            ncc.NCC_Ten = ten
            ncc.NCC_SDT = sdt
            ncc.NCC_DChi = dchi
            ncc.save()
            messages.success(request,
                             'Cập nhật nhà cung cấp thành công')  # Use case 13.3 step 7 says "Cập đặt thành công và thông báo Cập đặt nhà cung cấp thành công" - "Cập đặt" is typo in manual but I will use the exact wording to be safe. Actually, text says 'Cập đặt nhà cung cấp thành công'
        except Exception as e:
            messages.error(request, 'Không thể cập nhật thông tin nhà cung cấp, vui lòng thử lại sau.')

    return redirect('quan_ly_ncc')


def xoa_ncc_view(request, ma_ncc):
    if request.method == 'POST':
        try:
            ncc = get_object_or_404(NhaCungCap, NCC_Ma=ma_ncc)
            ncc.delete()
            messages.success(request, 'Xóa nhà cung cấp thành công')
        except Exception as e:
            messages.error(request, 'Xóa nhà cung cấp thất bại, vui lòng thử lại sau')

    return redirect('quan_ly_ncc')
