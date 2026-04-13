from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import ChiTietNhapHang

@receiver(pre_save, sender=ChiTietNhapHang)
def capture_old_quantity(sender, instance, **kwargs):
    """
    Lưu lại số lượng cũ trước khi cập nhật để tính toán chênh lệch.
    """


    if instance.pk:
        try:
            old_instance = ChiTietNhapHang.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.NH_SL
        except ChiTietNhapHang.DoesNotExist:
            instance._old_quantity = 0
    else:
        instance._old_quantity = 0



@receiver(post_save, sender=ChiTietNhapHang)
def update_stock_on_save(sender, instance, created, **kwargs):
    """
    Cập nhật SP_SL của BienTheSanPham khi thêm mới hoặc sửa đổi ChiTietNhapHang.
    """
    btsp = instance.BTSP_Ma
    if created:
        # Nếu tạo mới, cộng toàn bộ số lượng nhập
        btsp.SP_SL += instance.NH_SL
    else:
        # Nếu cập nhật, cộng vào phần chênh lệch (mới - cũ)
        old_qty = getattr(instance, '_old_quantity', 0)
        diff = instance.NH_SL - old_qty
        btsp.SP_SL += diff
    
    btsp.save()

@receiver(post_delete, sender=ChiTietNhapHang)
def update_stock_on_delete(sender, instance, **kwargs):
    """
    Trừ bớt SP_SL của BienTheSanPham khi xóa ChiTietNhapHang.
    """
    btsp = instance.BTSP_Ma
    btsp.SP_SL -= instance.NH_SL
    btsp.save()
