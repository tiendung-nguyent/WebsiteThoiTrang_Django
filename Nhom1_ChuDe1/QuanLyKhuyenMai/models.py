from django.db import models
from quanLySanPham.models import SanPham

class KhuyenMai(models.Model):
    KM_Ma = models.CharField(max_length=9, primary_key=True)
    KM_GiaTri = models.DecimalField(max_digits=10, decimal_places=2)
    KM_NgayBD = models.DateField()
    KM_NgayKT = models.DateField()
    KM_Ten = models.CharField(max_length=100)
    KM_Loai = models.CharField(max_length=50)

    def __str__(self):
        return self.KM_Ten

class SanPham_KhuyenMai(models.Model):
    SP_Ma = models.ForeignKey(SanPham, on_delete=models.CASCADE)
    KM_Ma = models.ForeignKey(KhuyenMai, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('SP_Ma', 'KM_Ma'),)

    def __str__(self):
        return f"{self.SP_Ma.SP_Ten} - KM: {self.KM_Ma.KM_Ten}"
