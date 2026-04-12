from django.shortcuts import render
def quanLyDonHang(request):
    return render(request, 'quanLyDonHang/quanLyDonHang.html')
def view_quanLyDonHang(request, status):
    context = {'status': status, 'order_id': 'ORD-2026-001'}
    return render(request, 'quanLyDonHang/view_quanLyDonHang.html', context)
