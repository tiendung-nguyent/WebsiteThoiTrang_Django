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

    # BƯỚC 1: Lấy TOÀN BỘ đơn hàng để xử lý cả tiền treo và trạng thái
    orders_qs = DonDat.objects.all().prefetch_related('donhangvanchuyen_set')
    all_orders = list(orders_qs)

    # Khởi tạo các biến chứa dữ liệu cho Thẻ (Cards)
    today_revenue = Decimal("0")
    today_count = 0
    tien_luan_chuyen = Decimal("0")

    # Khởi tạo biến đếm trạng thái đơn hàng trong Tháng này
    # Index tương ứng: 0 (Đang giao), 1 (Đã giao), 2 (Chờ xử lý), 3 (Thất bại)
    status_counts_dict = {0: 0, 1: 0, 2: 0, 3: 0}

    # BƯỚC 2: Phân loại và tính toán
    order_data_map = {}

    for order in all_orders:
        # --- 1. Thống kê trạng thái đơn hàng (Chỉ tính trong Tháng hiện tại) ---
        if order.TT_NgayDatHang.month == today.month and order.TT_NgayDatHang.year == today.year:
            if order.DH_TrangThai in status_counts_dict:
                status_counts_dict[order.DH_TrangThai] += 1

        # --- 2. Xử lý Thẻ: Tổng đơn hàng hôm nay ---
        if order.TT_NgayDatHang == today:
            today_count += 1

        # --- 3. Xử lý Thẻ: Tiền đang luân chuyển (Đơn Đang giao - Trạng thái 0) ---
        if order.DH_TrangThai == 0:
            tien_luan_chuyen += _decimal(order.TT_TongThanhToan)

        # --- 4. Xử lý Doanh thu & Lợi nhuận (CHỈ TÍNH ĐƠN ĐÃ GIAO - Trạng thái 1) ---
        if order.DH_TrangThai == 1:
            # Tính doanh thu đơn
            vanchuyen = order.donhangvanchuyen_set.first()
            phi_cuoc = vanchuyen.DH_PhiCuoc if vanchuyen else Decimal("0")
            doanh_thu_don = _decimal(order.TT_TongTienHang) + (_decimal(order.TT_TongPhiVC) - _decimal(phi_cuoc))

            # Tính giá vốn theo Chi tiết nhập hàng
            gia_von_don = Decimal("0")
            chi_tiet_ban = ChiTietGioHang.objects.filter(GH_Ma=order.GH_Ma)

            for item in chi_tiet_ban:
                ct_nhap = ChiTietNhapHang.objects.filter(BTSP_Ma=item.BTSP_Ma).last()
                don_gia_nhap = ct_nhap.NH_DonGia if ct_nhap else Decimal("0")
                gia_von_don += (item.GH_SL * don_gia_nhap)

            # Lưu vào map để vẽ biểu đồ Cột
            order_data_map[order.TT_Ma] = {
                'revenue': doanh_thu_don,
                'profit': doanh_thu_don - gia_von_don,
                'date': order.TT_NgayDatHang
            }

            # Cộng vào thẻ Doanh thu ngày nếu đơn được giao hôm nay
            if order.TT_NgayDatHang == today:
                today_revenue += doanh_thu_don

    # Chuyển đổi Dict trạng thái thành List theo đúng thứ tự mảng màu trên giao diện JS
    # [Cam (Đang giao), Xanh lá (Đã giao), Xanh dương (Chờ), Đỏ (Hủy)]
    status_counts = [
        status_counts_dict[0],
        status_counts_dict[1],
        status_counts_dict[2],
        status_counts_dict[3]
    ]

    # BƯỚC 3: Xử lý danh sách Top 5 Sản phẩm bán chạy (Tháng hiện tại)
    # Truy vấn đi từ: ChiTietGioHang -> GioHang -> DonDat để lọc trạng thái và ngày
    top_products = ChiTietGioHang.objects.filter(
        GH_Ma__dondat__DH_TrangThai=1,  # Chỉ tính sản phẩm của đơn đã giao thành công
        GH_Ma__dondat__TT_NgayDatHang__month=today.month,
        GH_Ma__dondat__TT_NgayDatHang__year=today.year
    ).values(
        'BTSP_Ma__SP_Ma__SP_Ten'  # Group by theo tên sản phẩm
    ).annotate(
        total_qty=Sum('GH_SL')  # Tính tổng số lượng
    ).order_by('-total_qty')[:5]  # Sắp xếp giảm dần và lấy 5

    # BƯỚC 4: Xây dựng dữ liệu biểu đồ Doanh thu (Hàm phụ trợ giữ nguyên)
    chart_data = _prepare_chart_data(order_data_map, today)

    context = {
        "current_date": today.strftime("%d/%m/%Y"),
        "daily_revenue": _currency(today_revenue),
        "new_orders_count": today_count,
        "tien_luan_chuyen": _currency(tien_luan_chuyen),
        "chart_data": chart_data,
        "status_counts": status_counts,
        "top_products": top_products,
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