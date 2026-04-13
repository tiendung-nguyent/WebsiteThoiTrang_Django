from collections import defaultdict
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg
from django.shortcuts import render
from django.utils import timezone

from donDat.models import DonDat
from gioHang.models import ChiTietGioHang
from QuanLyNhapHang.models import ChiTietNhapHang


def _decimal(value):
    return value if value is not None else Decimal("0")


def _currency(value):
    return f"{int(value):,} đ".replace(",", ".")


def _build_product_cost_map():
    cost_rows = (
        ChiTietNhapHang.objects
        .values("BTSP_Ma__SP_Ma")
        .annotate(avg_cost=Avg("NH_DonGia"))
    )

    return {
        row["BTSP_Ma__SP_Ma"]: _decimal(row["avg_cost"])
        for row in cost_rows
        if row["BTSP_Ma__SP_Ma"]
    }


def _build_order_cost_map(order_ids, product_cost_map):
    order_cost_map = defaultdict(lambda: Decimal("0"))
    order_rows = (
        ChiTietGioHang.objects
        .filter(GH_Ma_id__in=order_ids)
        .values("GH_Ma_id", "SP_Ma_id", "GH_SL")
    )

    for row in order_rows:
        unit_cost = product_cost_map.get(row["SP_Ma_id"], Decimal("0"))
        order_cost_map[row["GH_Ma_id"]] += unit_cost * Decimal(row["GH_SL"])

    return order_cost_map


def _build_period_chart_data(orders, order_cost_map, today):
    start_of_week = today - timedelta(days=today.weekday())
    week_labels = []
    week_revenue = []
    week_profit = []

    for offset in range(7):
        current_day = start_of_week + timedelta(days=offset)
        week_orders = [
            order for order in orders
            if order.TT_NgayDatHang == current_day
        ]
        revenue = sum((_decimal(order.TT_TongThanhToan) for order in week_orders), Decimal("0"))
        cost = sum((order_cost_map.get(order.GH_Ma_id, Decimal("0")) for order in week_orders), Decimal("0"))

        week_labels.append(f"Thứ {offset + 2}" if offset < 5 else ("Thứ 7" if offset == 5 else "Chủ Nhật"))
        week_revenue.append(float(revenue))
        week_profit.append(float(revenue - cost))

    month_labels = []
    month_revenue = []
    month_profit = []
    current_month_orders = [order for order in orders if order.TT_NgayDatHang.month == today.month and order.TT_NgayDatHang.year == today.year]

    days_in_month = (
        (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    ).day
    for day in range(1, days_in_month + 1):
        month_orders = [order for order in current_month_orders if order.TT_NgayDatHang.day == day]
        revenue = sum((_decimal(order.TT_TongThanhToan) for order in month_orders), Decimal("0"))
        cost = sum((order_cost_map.get(order.GH_Ma_id, Decimal("0")) for order in month_orders), Decimal("0"))

        month_labels.append(f"{day:02d}/{today.month:02d}")
        month_revenue.append(float(revenue))
        month_profit.append(float(revenue - cost))

    quarter = ((today.month - 1) // 3) + 1
    start_month = (quarter - 1) * 3 + 1
    quarter_labels = []
    quarter_revenue = []
    quarter_profit = []

    for month in range(start_month, start_month + 3):
        quarter_orders = [
            order for order in orders
            if order.TT_NgayDatHang.year == today.year and order.TT_NgayDatHang.month == month
        ]
        revenue = sum((_decimal(order.TT_TongThanhToan) for order in quarter_orders), Decimal("0"))
        cost = sum((order_cost_map.get(order.GH_Ma_id, Decimal("0")) for order in quarter_orders), Decimal("0"))

        quarter_labels.append(f"Tháng {month}")
        quarter_revenue.append(float(revenue))
        quarter_profit.append(float(revenue - cost))

    return {
        "week": {
            "labels": week_labels,
            "revenue": week_revenue,
            "profit": week_profit,
        },
        "month": {
            "labels": month_labels,
            "revenue": month_revenue,
            "profit": month_profit,
        },
        "quarter": {
            "labels": quarter_labels,
            "revenue": quarter_revenue,
            "profit": quarter_profit,
        },
    }


def bao_cao_view(request):
    today = timezone.localdate()
    all_orders = list(
        DonDat.objects.all().only(
            "TT_Ma",
            "GH_Ma",
            "TT_TongThanhToan",
            "TT_TongTienHang",
            "TT_NgayDatHang",
        )
    )

    product_cost_map = _build_product_cost_map()
    order_cost_map = _build_order_cost_map(
        [order.GH_Ma_id for order in all_orders],
        product_cost_map,
    )

    today_orders = [order for order in all_orders if order.TT_NgayDatHang == today]
    daily_revenue = sum((_decimal(order.TT_TongThanhToan) for order in today_orders), Decimal("0"))
    daily_cost = sum((order_cost_map.get(order.GH_Ma_id, Decimal("0")) for order in today_orders), Decimal("0"))
    daily_profit = daily_revenue - daily_cost

    chart_data = _build_period_chart_data(all_orders, order_cost_map, today)

    context = {
        "current_date": today.strftime("%d/%m/%Y"),
        "daily_revenue": _currency(daily_revenue),
        "new_orders_count": len(today_orders),
        "daily_profit": _currency(daily_profit),
        "chart_data": chart_data,
    }
    return render(request, "BaoCaoThongKe/BaoCaoThongKe.html", context)
