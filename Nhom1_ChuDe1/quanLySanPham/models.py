from django.db import models
from QuanLyDanhMuc.models import DanhMuc

class SanPham(models.Model):
    TRANG_THAI_CHOICES = [
        (0, 'Đang bán'),
        (1, 'Hết hàng'),
        (2, 'Ngừng bán'),
    ]

    SP_Ma = models.CharField(max_length=10, primary_key=True)
    DM_Ma = models.ForeignKey(DanhMuc, on_delete=models.CASCADE, related_name='san_pham_thuoc_dm')
    SP_Ten = models.CharField(max_length=100)
    SP_GiaBan = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    SP_MoTa = models.TextField(null=True, blank=True)
    SP_URLHinhAnh = models.URLField(max_length=500, null=True, blank=True)

    SP_TrangThai = models.IntegerField(
        choices=TRANG_THAI_CHOICES,
        default=0
    )

    def __str__(self):
        return self.SP_Ten

class BienTheSanPham(models.Model):
    BTSP_Ma = models.CharField(max_length=9, primary_key=True)
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    SP_SL = models.IntegerField(default=0)
    SP_KichThuoc = models.CharField(max_length=5)
    SP_MauSac = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.BTSP_Ma} - {self.SP_KichThuoc} - {self.SP_MauSac}"
