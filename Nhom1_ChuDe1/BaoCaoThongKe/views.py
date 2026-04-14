from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from django.db.models import Sum, F
from django.shortcuts import render
from django.utils import timezone
from donDat.models import DonDat
from gioHang.models import ChiTietGioHang
from QuanLyNhapHang.models import ChiTietNhapHang


def _decimal(value):
    return value if value is not None else Decimal("0")


def _currency(value):
    return f"{int(value):,} đ".replace(",", ".")


def bao_cao_view(request):
    today = timezone.localdate()

    # BƯỚC 1: Lọc đơn hàng "Đã giao" (giá trị là 1)
    orders_qs = DonDat.objects.filter(DH_TrangThai=1).prefetch_related('donhangvanchuyen_set')
    all_orders = list(orders_qs)

    # BƯỚC 2: Tính doanh thu = Tiền hàng + (Phí thu khách - Phí trả đơn vị VC)
    order_data_map = {}
    for order in all_orders:
        # Lấy phí cước từ bảng DonHangVanChuyen liên kết qua TT_Ma
        vanchuyen = order.donhangvanchuyen_set.first()
        phi_cuoc = vanchuyen.DH_PhiCuoc if vanchuyen else Decimal("0")

        doanh_thu_don = _decimal(order.TT_TongTienHang) + (_decimal(order.TT_TongPhiVC) - _decimal(phi_cuoc))

        # BƯỚC 3: Tính giá vốn theo Chi tiết nhập hàng
        gia_von_don = Decimal("0")
        chi_tiet_ban = ChiTietGioHang.objects.filter(GH_Ma=order.GH_Ma)

        for item in chi_tiet_ban:
            ct_nhap = ChiTietNhapHang.objects.filter(
                BTSP_Ma=item.BTSP_Ma).last()
            don_gia_nhap = ct_nhap.NH_DonGia if ct_nhap else Decimal("0")
            gia_von_don += (item.GH_SL * don_gia_nhap)

        order_data_map[order.TT_Ma] = {
            'revenue': doanh_thu_don,
            'profit': doanh_thu_don - gia_von_don,
            'date': order.TT_NgayDatHang
        }

    # BƯỚC 4: Tổng hợp dữ liệu cho Ngày hôm nay
    today_revenue = Decimal("0")
    today_profit = Decimal("0")
    today_count = 0

    for m_id, data in order_data_map.items():
        if data['date'] == today:
            today_revenue += data['revenue']
            today_profit += data['profit']
            today_count += 1

    # BƯỚC 5: Xây dựng dữ liệu biểu đồ
    chart_data = _prepare_chart_data(order_data_map, today)

    context = {
        "current_date": today.strftime("%d/%m/%Y"),
        "daily_revenue": _currency(today_revenue),
        "new_orders_count": today_count,
        "daily_profit": _currency(today_profit),
        "chart_data": chart_data,
    }
    return render(request, "BaoCaoThongKe/BaoCaoThongKe.html", context)


def _prepare_chart_data(order_data_map, today):
    # --- 1. XỬ LÝ TUẦN ---
    start_of_week = today - timedelta(days=today.weekday())
    week_labels, week_rev, week_prof = [], [], []
    day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

    for i in range(7):
        curr = start_of_week + timedelta(days=i)
        day_rev = sum(d['revenue'] for d in order_data_map.values() if d['date'] == curr)
        day_prof = sum(d['profit'] for d in order_data_map.values() if d['date'] == curr)
        week_labels.append(day_names[i])
        week_rev.append(float(day_rev))
        week_prof.append(float(day_prof))

    # --- 2. XỬ LÝ THÁNG ---
    import calendar
    month_labels, month_rev, month_prof = [], [], []
    # Lấy số ngày trong tháng hiện tại
    num_days = calendar.monthrange(today.year, today.month)[1]

    for day in range(1, num_days + 1):
        curr_date = today.replace(day=day)
        day_rev = sum(d['revenue'] for d in order_data_map.values() if d['date'] == curr_date)
        day_prof = sum(d['profit'] for d in order_data_map.values() if d['date'] == curr_date)
        month_labels.append(f"{day:02d}/{today.month:02d}")
        month_rev.append(float(day_rev))
        month_prof.append(float(day_prof))

    # --- 3. XỬ LÝ QUÝ ---
    quarter_labels, quarter_rev, quarter_prof = [], [], []
    current_quarter = (today.month - 1) // 3 + 1
    start_month = (current_quarter - 1) * 3 + 1

    for m in range(start_month, start_month + 3):
        # Tính tổng cả tháng
        m_rev = sum(d['revenue'] for d in order_data_map.values()
                    if d['date'].month == m and d['date'].year == today.year)
        m_prof = sum(d['profit'] for d in order_data_map.values()
                     if d['date'].month == m and d['date'].year == today.year)
        quarter_labels.append(f"Tháng {m}")
        quarter_rev.append(float(m_rev))
        quarter_prof.append(float(m_prof))

    return {
        "week": {"labels": week_labels, "revenue": week_rev, "profit": week_prof},
        "month": {"labels": month_labels, "revenue": month_rev, "profit": month_prof},
        "quarter": {"labels": quarter_labels, "revenue": quarter_rev, "profit": quarter_prof},
    }