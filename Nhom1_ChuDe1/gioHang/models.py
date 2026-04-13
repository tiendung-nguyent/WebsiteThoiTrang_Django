from django.db import models
from QuanLyKhachHang.models import KhachHang
from quanLySanPham.models import SanPham

class GioHang(models.Model):
    GH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ma = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    GH_TongSL = models.IntegerField(default=0)
    GH_TamTinh = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.GH_Ma

class ChiTietGioHang(models.Model):
    GH_Ma = models.ForeignKey(GioHang, on_delete=models.CASCADE)
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    GH_SL = models.IntegerField(default=1)
    GH_TTien = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('GH_Ma', 'SP_Ma'),)

    def __str__(self):
        return f"{self.SP_Ma.SP_Ten} trong giỏ {self.GH_Ma.GH_Ma} (SL: {self.GH_SL})"
