from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import DonDat
from gioHang.models import ChiTietGioHang

@receiver(post_save, sender=DonDat)
def quan_ly_kho(sender, instance, created, **kwargs):
    don_hang = instance
    """
    Tu dong quan ly kho dua tren trang thai DonDat.
    - Trang thai 0, 1, 2: Giam so luong trong kho.
    - Trang thai 3: Hoan lai so luong vao kho.
    """
    # Cac trang thai duoc coi la "Da tru kho"
    TRANG_THAI_GIAM_KHO = [0, 1, 2]
    TRANG_THAI_HOAN_KHO = 3
    
    # Lay trang thai hien tai cua don hang
    trang_thai_hien_tai = don_hang.DH_TrangThai
    
    # Lay trang thai truoc do (duoc luu tu pre_save)
    trang_thai_truoc_do = getattr(don_hang, '_trang_thai_truoc_do', None)

    danh_sach_san_pham = ChiTietGioHang.objects.filter(GH_Ma=don_hang.GH_Ma)

    def cap_nhat_so_luong(tang_so_luong=True):
        for chi_tiet in danh_sach_san_pham:
            bien_the = chi_tiet.BTSP_Ma
            if tang_so_luong:
                bien_the.SP_SL += chi_tiet.GH_SL
            else:
                bien_the.SP_SL -= chi_tiet.GH_SL
            bien_the.save()

            # Tự động cập nhật trạng thái Sản phẩm thành 'Hết hàng' (1) nếu không còn biến thể nào còn hàng
            sp = bien_the.SP_Ma
            if sp.SP_TrangThai == 0:
                from quanLySanPham.models import BienTheSanPham
                if not BienTheSanPham.objects.filter(SP_Ma=sp, SP_SL__gt=0).exists():
                    sp.SP_TrangThai = 1
                    sp.save()

    if created:
        # Neu don hang moi tao co trang thai can giam kho thi tru kho ngay
        if trang_thai_hien_tai in TRANG_THAI_GIAM_KHO:
            cap_nhat_so_luong(tang_so_luong=False)
    else:
        # Neu trang thai thay doi tu (0, 1, 2) sang (3) -> Tang lai kho
        if trang_thai_truoc_do in TRANG_THAI_GIAM_KHO and trang_thai_hien_tai == TRANG_THAI_HOAN_KHO:
            cap_nhat_so_luong(tang_so_luong=True)
        # Neu trang thai thay doi tu (3) quay lai (0, 1, 2) -> Tru lai kho
        elif trang_thai_truoc_do == TRANG_THAI_HOAN_KHO and trang_thai_hien_tai in TRANG_THAI_GIAM_KHO:
            cap_nhat_so_luong(tang_so_luong=False)



@receiver(pre_save, sender=DonDat)
def luu_trang_thai_truoc_do(sender, instance, **kwargs):
    don_hang = instance
    """
    Luu lai trang thai cua don hang truoc khi update de so sanh.
    """
    if don_hang.pk:
        try:
            don_hang_cu = DonDat.objects.get(pk=don_hang.pk)
            don_hang._trang_thai_truoc_do = don_hang_cu.DH_TrangThai
        except DonDat.DoesNotExist:
            don_hang._trang_thai_truoc_do = None
    else:
        don_hang._trang_thai_truoc_do = None
