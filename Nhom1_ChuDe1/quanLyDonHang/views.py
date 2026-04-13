from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from donDat.models import DonDat
from .models import DonHangVanChuyen
from gioHang.models import ChiTietGioHang

def quanLyDonHang(request):
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')

    orders = DonDat.objects.all().order_by('-TT_Ma')

    if query:
        orders = orders.filter(
            Q(TT_Ma__icontains=query) |
            Q(CTKH_Ma__CTKH_HoTenNguoiNhan__icontains=query) |
            Q(CTKH_Ma__CTKH_SDT__icontains=query)
        )

    if status and status != 'all':
        orders = orders.filter(DH_TrangThai=status)

    return render(request, 'quanLyDonHang/quanLyDonHang.html', {
        'orders': orders,
        'query': query,
        'status': status
    })

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

    if order.DH_TrangThai == 3:
        # Với đơn thất bại: Lợi nhuận = Tiền ship - Tiền ship thực tế
        actual_shipping = shipping_info.DH_PhiCuoc if shipping_info else 0
        profit = order.TT_TongPhiVC - actual_shipping
    else:
        # Lợi nhuận bình thường
        actual_shipping = shipping_info.DH_PhiCuoc if shipping_info else 0
        profit = order.TT_TongThanhToan - actual_shipping

    # Tính tiền giảm giá
    discount_amount = (order.TT_TongTienHang + order.TT_TongPhiVC) - order.TT_TongThanhToan
    if discount_amount < 0: discount_amount = 0

    context = {
        'order': order,
        'order_items': order_items,
        'shipping_info': shipping_info,
        'status': status_str, # Keep this for template compatibility
        'order_id': order.TT_Ma,
        'profit': profit,
        'discount_amount': discount_amount
    }
    return render(request, 'quanLyDonHang/view_quanLyDonHang.html', context)
