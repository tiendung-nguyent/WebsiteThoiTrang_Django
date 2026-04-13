from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import DonDat
from gioHang.models import ChiTietGioHang


def quanLyDonDat(request):
    ds_don = DonDat.objects.all().order_by('-TT_NgayDatHang', '-TT_Ma')

    for don in ds_don:
        don.ds_san_pham = ChiTietGioHang.objects.filter(GH_Ma=don.GH_Ma)
        print("DON:", don.TT_Ma, "GH:", don.GH_Ma, "SO SP:", don.ds_san_pham.count())

    return render(request, 'donDat/quanLyDonDat.html', {
        'ds_don': ds_don
    })


def huyDonDat(request, tt_ma):
    don = get_object_or_404(DonDat, TT_Ma=tt_ma)

    if request.method == 'POST':
        if don.DH_TrangThai != 2:
            messages.error(request, 'Chỉ được hủy đơn khi đơn đang ở trạng thái Chờ xử lý.')
            return redirect('quanLyDonDat')

        don.DH_TrangThai = 3
        don.save()

        messages.success(request, 'Hủy đơn thành công.')
        return redirect('quanLyDonDat')

    return redirect('quanLyDonDat')