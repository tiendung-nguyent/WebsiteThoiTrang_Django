from django.shortcuts import render, get_object_or_404, redirect
from donDat.models import DonDat
from .models import DonHangVanChuyen
from gioHang.models import ChiTietGioHang

def quanLyDonHang(request):
    orders = DonDat.objects.all().order_by('-TT_Ma')
    return render(request, 'quanLyDonHang/quanLyDonHang.html', {'orders': orders})

def view_quanLyDonHang(request, order_id):
    order = get_object_or_404(DonDat, TT_Ma=order_id)
    order_items = ChiTietGioHang.objects.filter(GH_Ma=order.GH_Ma)
    shipping_info = DonHangVanChuyen.objects.filter(TT_Ma=order).first()

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'ship':
            tracking_code = request.POST.get('tracking_code')
            shipping_unit = request.POST.get('shipping_unit')
            shipping_fee = request.POST.get('shipping_fee')
            
            # Create or update shipping info
            DonHangVanChuyen.objects.update_or_create(
                TT_Ma=order,
                defaults={
                    'DH_MaVanChuyen': tracking_code,
                    'DH_DViVanChuyen': shipping_unit,
                    'DH_PhiCuoc': shipping_fee
                }
            )
            # Update status to "Đang giao" (0)
            order.DH_TrangThai = 0
            order.save()
            return redirect('view_quanLyDonHang', order_id=order_id)
            
        elif action == 'cancel':
            order.DH_TrangThai = 3 # Thất bại / Đã hủy 
            order.save()
            return redirect('view_quanLyDonHang', order_id=order_id)
            
        elif action == 'complete':
            order.DH_TrangThai = 1 # Đã giao
            order.save()
            return redirect('view_quanLyDonHang', order_id=order_id)
            
        elif action == 'fail':
            order.DH_TrangThai = 3 # Thất bại
            order.save()
            return redirect('view_quanLyDonHang', order_id=order_id)

    # Map status code to the string used in template logic if needed, 
    # but we can also change template to use codes.
    # Current template uses: 'cho_xu_ly', 'dang_giao', 'da_huy', 'da_giao'
    status_map = {
        2: 'cho_xu_ly',
        0: 'dang_giao',
        3: 'da_huy',
        1: 'da_giao'
    }
    status_str = status_map.get(order.DH_TrangThai, 'cho_xu_ly')

    profit = order.TT_TongThanhToan
    if shipping_info:
        profit -= shipping_info.DH_PhiCuoc

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_info': shipping_info,
        'status': status_str, # Keep this for template compatibility
        'order_id': order.TT_Ma,
        'profit': profit
    }
    return render(request, 'quanLyDonHang/view_quanLyDonHang.html', context)
