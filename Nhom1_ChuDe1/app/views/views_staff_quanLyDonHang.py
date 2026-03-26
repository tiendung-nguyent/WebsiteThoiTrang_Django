from django.shortcuts import render

def quanLyDonHang(request):
    return render(request, 'staff/quanLyDonHang/quanLyDonHang.html')
def view_quanLyDonHang(request, status):
    """
    View chung cho tất cả trạng thái đơn hàng
    status nhận các giá trị: 'cho_xu_ly', 'dang_giao', 'da_giao', 'da_huy'
    """
    context = {
        'status': status,
        'order_id': 'ORD-2026-001', # Sau này sẽ lấy từ DB dựa trên ID
    }
    return render(request, 'staff/quanLyDonHang/view_quanLyDonHang.html', context)