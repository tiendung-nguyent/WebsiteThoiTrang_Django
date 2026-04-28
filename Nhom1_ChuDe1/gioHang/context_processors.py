from gioHang.models import GioHang
from quanLyKhachHang.models import KhachHang

def cart_count_processor(request):
    if request.user.is_authenticated:
        try:
            kh_ma = f"KH{request.user.id:07d}"
            kh = KhachHang.objects.get(KH_Ma=kh_ma)
            gio_hang = GioHang.objects.filter(KH_Ma=kh, dondat__isnull=True).last()
            if gio_hang:
                return {'cart_count': gio_hang.GH_TongSL}
        except KhachHang.DoesNotExist:
            pass
    return {'cart_count': 0}
