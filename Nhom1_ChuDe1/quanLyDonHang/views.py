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

import requests
import re
from datetime import datetime

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
            
            DonHangVanChuyen.objects.update_or_create(
                TT_Ma=order,
                defaults={
                    'DH_MaVanChuyen': tracking_code,
                    'DH_DViVanChuyen': shipping_unit,
                    'DH_PhiCuoc': shipping_fee
                }
            )
            order.DH_TrangThai = 0
            
            # --- Tính lại Ngày giao hàng dự kiến qua GHN ---
            try:
                GHN_TOKEN = "dc8f38d8-4509-11f1-bc69-ee9455d43f1a"
                SHOP_ID = "6412169"
                FROM_DISTRICT_ID = 1454
                FROM_WARD_CODE = "21211"
                headers = {
                    'Token': GHN_TOKEN,
                    'ShopId': SHOP_ID,
                    'Content-Type': 'application/json'
                }
                address_str = order.CTKH_Ma.CTKH_DiaChi if order.CTKH_Ma else ""
                if address_str:
                    addr_lower = address_str.lower()
                    
                    # 1. TÌM QUẬN/HUYỆN
                    res_district = requests.get("https://online-gateway.ghn.vn/shiip/public-api/master-data/district", headers=headers).json()
                    districts = res_district.get('data') or []
                    target_district_id = None
                    for d in districts:
                        d_name = d.get('DistrictName', '')
                        if not d_name: continue
                        clean_name = re.sub(r'^(Huyện|Quận|Thành phố|Thị xã|Tỉnh)\s+', '', d_name, flags=re.IGNORECASE)
                        if clean_name.lower() in addr_lower:
                            target_district_id = d.get('DistrictID')
                            break
                    
                    if target_district_id:
                        # 2. TÌM PHƯỜNG/XÃ
                        res_ward = requests.get(f"https://online-gateway.ghn.vn/shiip/public-api/master-data/ward?district_id={target_district_id}", headers=headers).json()
                        wards = res_ward.get('data') or []
                        target_ward_code = None
                        for w in wards:
                            w_name = w.get('WardName', '')
                            if not w_name: continue
                            clean_w_name = re.sub(r'^(Phường|Xã|Thị trấn)\s+', '', w_name, flags=re.IGNORECASE)
                            if clean_w_name.lower() in addr_lower:
                                target_ward_code = w.get('WardCode')
                                break
                        if not target_ward_code and len(wards) > 0:
                            target_ward_code = wards[0].get('WardCode')
                        
                        if target_ward_code:
                            # 3. TÍNH LEADTIME TỪ HÔM NAY
                            payload = {
                                "from_district_id": FROM_DISTRICT_ID,
                                "from_ward_code": FROM_WARD_CODE,
                                "to_district_id": target_district_id,
                                "to_ward_code": target_ward_code,
                                "service_id": 53320
                            }
                            res_leadtime = requests.post("https://online-gateway.ghn.vn/shiip/public-api/v2/shipping-order/leadtime", json=payload, headers=headers).json()
                            if res_leadtime.get('code') == 200:
                                expected_ts = res_leadtime['data']['leadtime']
                                order.TT_NgayGiaoDuKien = datetime.fromtimestamp(expected_ts).date()
            except Exception as e:
                pass # Bỏ qua nếu có lỗi kết nối GHN
            # -----------------------------------------------

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
