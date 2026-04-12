from django.db import models

class NhapHang(models.Model):
    NH_Ma = models.CharField(max_length=9, primary_key=True)
    NCC_Ma = models.ForeignKey('QuanLyNhaCungCap.NhaCungCap', on_delete=models.CASCADE)
    NH_Ngay = models.DateField(auto_now_add=True)
    NH_TongTien = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.NH_Ma

class ChiTietNhapHang(models.Model):
    BTSP_Ma = models.ForeignKey('quanLySanPham.BienTheSanPham', on_delete=models.CASCADE)
    NH_Ma = models.ForeignKey(NhapHang, on_delete=models.CASCADE)
    NH_DonGia = models.DecimalField(max_digits=10, decimal_places=2)
    NH_SL = models.IntegerField()
    NH_TTien = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = (('BTSP_Ma', 'NH_Ma'),)
