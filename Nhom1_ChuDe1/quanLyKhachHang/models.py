from django.db import models

class KhachHang(models.Model):
    KH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ten = models.CharField(max_length=100)
    KH_TongChiTieu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    KH_SoDonHang = models.IntegerField(default=0)

    def __str__(self):
        return self.KH_Ten


class ChiTietKhachHang(models.Model):
    CTKH_Ma = models.CharField(max_length=9, primary_key=True)
    KH_Ma = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    CTKH_HoTenNguoiNhan = models.CharField(max_length=100)
    CTKH_SDT = models.CharField(max_length=10)
    CTKH_DiaChi = models.TextField()

    def __str__(self):
        return f"{self.CTKH_HoTenNguoiNhan} - {self.CTKH_Ma}"
